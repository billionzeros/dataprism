package chatService

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/OmGuptaIND/shooting-star/appError"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/db"
	"github.com/OmGuptaIND/shooting-star/db/models"
	"github.com/OmGuptaIND/shooting-star/provider"
	"github.com/OmGuptaIND/shooting-star/provider/tools"
	"github.com/google/generative-ai-go/genai"
	"go.uber.org/zap"
)


type chatService struct {
	ctx context.Context

	// GenerativeModel is the generative model used for chat interactions.
	generativeModel *genai.GenerativeModel

	// EmbeddingModel is the embedding model used for generating embeddings.
	embeddingModel *genai.EmbeddingModel

	// ChatSession is the chat session for the current conversation.
	chatSession *genai.ChatSession

	// Logger is the logger instance for logging messages.
	logger *zap.Logger

	// WorkspaceId is the ID of the workspace associated with the chat.
	workspaceId string
}

// ChatService defines the interface for chat-related operations.
type ChatService interface {
	// Push a new message to the chat.
	PushNewChat(message *ChatMessage) (*ChatMessage, error)
}


// NewDocumentService creates a new instance of DocumentService with the provided logger.
func NewChatService(ctx context.Context, workspaceId string) (ChatService, error) {
	gemini, err := provider.NewGeminiProvider(ctx)
	if err != nil {
		return nil, err
	}
	
	gm := gemini.GenerativeModel(string(provider.Gemini1_5ProLatest))

	gm.Tools = []*genai.Tool{
		tools.SearchRelevantDocumentsTool,
		tools.ExecuteDataQueryTool,
	}

	em := gemini.EmbeddingModel(string(provider.Embedding001))

	gm.SystemInstruction = &genai.Content{
        Parts: []genai.Part{genai.Text(fmt.Sprintf(`
            Context:
                WorkspaceId: %s

            Instructions:
            You are a helpful assistant analyzing CSV data in the specified workspace.

            **Workflow:**
            1.  **Understand the Goal:** Determine what specific information or calculation the user is asking for.
            2.  **Discover Relevant Data:** Use the 'search_relevant_documents' tool first to find relevant column names, descriptions, and upload IDs based on the user's request. Provide a concise 'query_text'.
            3.  **Analyze Discovery Results:** Wait for the 'search_results_json' from 'search_relevant_documents'. Examine the results to confirm you have the correct column names and understand the data structure.
            4.  **Plan Next Step:**
                *   If the user's question can be answered directly from the column names/descriptions found (e.g., "What columns have location info?"), proceed to step 6.
                *   If the user's question requires retrieving specific values, filtering data, or performing calculations (e.g., "Where are most sellers from?", "What is the total sales?"), **you MUST proceed to step 5.**
            5.  **Execute Data Query:** Formulate a query string (use standard SQL syntax, referencing column names exactly as found in the search results). Call the 'execute_data_query' tool with the 'query_string'. If specific 'upload_ids' were identified in step 3, include them in the 'upload_ids' parameter. Wait for the results from 'execute_data_query'.
            6.  **Synthesize Final Answer:** Based on the information gathered (either from 'search_relevant_documents' results directly OR from 'execute_data_query' results), formulate a clear and concise answer for the user. Explain how you arrived at the answer, referencing the tools used and data points found.
            7.  **Handle Errors/Missing Data:** If tools return errors or no relevant data is found at any stage, inform the user clearly. Do not invent information.
        `, workspaceId))},
    }

	chatSession := gm.StartChat()

	return &chatService{
		ctx: ctx,
		generativeModel: gm,
		embeddingModel: em,
		chatSession: chatSession,
		logger: logger.FromCtx(ctx),
		workspaceId: workspaceId,
	}, nil
}

// PushNewChat adds a new message to the chat.
func (c *chatService) PushNewChat(chat *ChatMessage) (*ChatMessage, error) {
	c.logger.Info("Adding new message to chat", zap.String("message", chat.Message), zap.String("role", string(chat.Role)))

	ctx, cancel := context.WithTimeout(c.ctx, 20*time.Second)
	defer cancel()

	resp, err := c.chatSession.SendMessage(ctx, genai.Text(chat.Message))
	if err != nil {
		c.logger.Error("Error sending message", zap.Error(err))
		return nil, appError.New(appError.InternalError, err.Error(), err)
	}

	c.logger.Sugar().Info("Received response from LLM", resp.Candidates[0].FunctionCalls())

	for {
        fc := getFunctionCall(resp)
        if fc == nil {
            c.logger.Info("No function call detected, proceeding to final response.")
            break
        }

        c.logger.Info("Function call detected, handling...", zap.String("function_name", fc.Name))


        nextResponse, err := c.handleFunctionCall(ctx, fc)
        if err != nil {
            c.logger.Error("Error handling function call", zap.Error(err))
            return nil, appError.New(appError.InternalError, "failed during function call execution", err)
        }

        resp = nextResponse
        c.logger.Debug("Received response after handling function call, checking for next action.")
    }

	assistantResponse := extractTextResponse(resp)
	if assistantResponse == "" {
        c.logger.Warn("LLM response was empty or contained no text part after potential function call")
        assistantResponse = "I received a response, but it contained no text content."
    }

	responseMessage := &ChatMessage{
		ChatId: chat.ChatId,
		Message: assistantResponse,
		Role: AssistantRole,
		Timestamp: time.Now().Format(time.RFC3339),
	}

	return responseMessage, nil
}

// getFunctionCall checks if the response contains a function call part.
func getFunctionCall(resp *genai.GenerateContentResponse) *genai.FunctionCall {
    if resp == nil || len(resp.Candidates) == 0 {
        return nil
    }

    calls := resp.Candidates[0].FunctionCalls()

    if len(calls) > 0 {

        if len(calls) > 1 {
            	fmt.Printf("Warning: Multiple function calls received (%d), processing only the first: %s\n", len(calls), calls[0].Name)
        }
        return &calls[0]
    }

    return nil
}


// handleFunctionCall handles the function call and executes the appropriate logic.
func (c *chatService) handleFunctionCall(ctx context.Context, fc *genai.FunctionCall) (*genai.GenerateContentResponse, error) {
	c.logger.Info("Handling Function Call", zap.String("function_name", fc.Name))

	// Execute the function call and get the response
	funcResp, err := c.executeFunctionCall(fc)
	if err != nil {
		c.logger.Error("Error executing function call", zap.String("fc_name", fc.Name), zap.Error(err))

		funcResp = &genai.FunctionResponse{
			Name: fc.Name,
			Response: map[string]interface{}{
				"error": fmt.Sprintf("Error executing function call: %v", err),
			},
		}
	}

	// Send the function call response back to the chat session
	llmResp, err := c.chatSession.SendMessage(ctx, funcResp)
	if err != nil {
		c.logger.Error("Error sending function call response", zap.Error(err))
		return nil, appError.New(appError.InternalError, err.Error(), err)
	}

	c.logger.Info("Function call response sent", zap.String("function_name", fc.Name))

	return llmResp, err
}

// handleSearchRelevantDocuments executes the actual search logic.
func (c *chatService) handleSearchRelevantDocuments(fc *genai.FunctionCall) (*genai.FunctionResponse, error) {
    queryText, ok := fc.Args["query_text"].(string)
    if !ok || queryText == "" {
        return nil, fmt.Errorf("missing or invalid 'query_text' argument")
    }

    c.logger.Info("Executing search_relevant_documents", zap.String("query_text", queryText))

	var relevantUploadIds []string
    err := db.Conn.Model(&models.WorkspaceUpload{}).
        Where("workspace_id = ?", c.workspaceId).
        Pluck("upload_id", &relevantUploadIds).Error
    if err != nil {
        c.logger.Error("Failed to fetch relevant upload IDs for workspace", zap.Error(err), zap.String("workspaceId", c.workspaceId))
        return nil, fmt.Errorf("failed to retrieve uploads for workspace: %w", err)
    }

    if len(relevantUploadIds) == 0 {
        c.logger.Warn("No uploads found linked to this workspace", zap.String("workspaceId", c.workspaceId))
        return &genai.FunctionResponse{
            Name: fc.Name,
            Response: map[string]interface{}{
                "search_results": []map[string]interface{}{},
                "message":        "No relevant documents found in this workspace.",
            },
        }, nil
    }

    embedCtx, cancel := context.WithTimeout(c.ctx, 15*time.Second)
    defer cancel()
	
	embedRes, err := c.embeddingModel.EmbedContent(embedCtx, genai.Text(queryText))
    if err != nil {
        return nil, fmt.Errorf("failed to embed query text: %w", err)
    }
    
	if embedRes.Embedding == nil || len(embedRes.Embedding.Values) == 0 {
        return nil, fmt.Errorf("embedding model returned empty vector")
    }

    queryVector := embedRes.Embedding.Values

    var results []struct {
        models.VectorEmbedding
        Similarity float64 `gorm:"column:similarity"`
    }
    limit := 5

    err = db.Conn.Table("vector_embeddings").
        Select("*, 1 - (embedding <=> ?) AS similarity", models.PgVector(queryVector)).
        Where("source_identifier IN ?", relevantUploadIds).
        Where("source_type = ?", models.EmbeddingSourceTypeCSVColumn).
        Order("similarity DESC").
        Limit(limit).
        Find(&results).Error
    if err != nil {
        return nil, fmt.Errorf("database vector search failed: %w", err)
    }

	formattedResultsMaps := make([]map[string]interface{}, 0, len(results))
    for _, res := range results {
        resultMap := map[string]interface{}{
            "upload_id":       res.SourceIdentifier, // Corrected field name
            "column_name":     res.ColumnOrChunkName,
            "content_snippet": res.OriginalText,
            "relevance_score": res.Similarity,
        }
        formattedResultsMaps = append(formattedResultsMaps, resultMap)
    }

    // --- 5. Marshal the Entire Slice into ONE JSON String ---
    var resultsJSONString string
    if len(formattedResultsMaps) > 0 {
        jsonBytes, err := json.Marshal(formattedResultsMaps)
        if err != nil {
            c.logger.Error("Failed to marshal results slice to JSON", zap.Error(err))
            resultsJSONString = `{"error": "Failed to format search results"}`
        } else {
            resultsJSONString = string(jsonBytes)
        }
    } else {
        resultsJSONString = `{"search_results": []}`
    }

	c.logger.Info("Search results found and formatted as JSON string", zap.Int("count", len(formattedResultsMaps)))
    c.logger.Info("Search results JSON string", zap.String("results_json", resultsJSONString))

    return &genai.FunctionResponse{
        Name: fc.Name,
        Response: map[string]interface{}{
            "search_results": resultsJSONString,
        },
    }, nil
}

func (c *chatService) handleExecuteDataQuery(fc *genai.FunctionCall) (*genai.FunctionResponse, error) {
    queryString, ok := fc.Args["query_string"].(string)
    uploadIDsArg := fc.Args["upload_ids"]

    var uploadIDs []string
    if uploadIDsArg != nil {
        if ids, ok := uploadIDsArg.([]interface{}); ok {
            for _, item := range ids {
                if idStr, ok := item.(string); ok {
                    uploadIDs = append(uploadIDs, idStr)
                }
            }
        }
    }


    if !ok || queryString == "" {
        // Return error *response* to LLM
        return &genai.FunctionResponse{
            Name: fc.Name,
            Response: map[string]interface{}{
                "error": "Missing or invalid 'query_string' argument.",
            },
        }, nil
    }

    c.logger.Info("Executing data query", zap.String("query", queryString), zap.Strings("upload_ids", uploadIDs))

    queryResultText := fmt.Sprintf("Placeholder Result for Query: '%s'. (Query execution logic needs implementation using a library like DuckDB on file paths associated with Upload IDs: %v)", queryString, uploadIDs)
    c.logger.Warn("Data query execution is not fully implemented.", zap.String("query", queryString))

    return &genai.FunctionResponse{
        Name: fc.Name,
        Response: map[string]interface{}{
            "query_result_text": queryResultText,
        },
    }, nil
}

// ExecuteFunctionCall executes a function call based on the provided function call object.
func (c *chatService) executeFunctionCall(fc *genai.FunctionCall) (*genai.FunctionResponse, error) {
	switch fc.Name {
		case string(tools.SearchRelevantDocumentsToolType):
			return c.handleSearchRelevantDocuments(fc)
		case string(tools.ExecuteDataQueryToolType):
			return c.handleExecuteDataQuery(fc)
		
		default:
			return nil, appError.New(appError.BadRequest, "Invalid function call", nil)
	}
}

// extractTextResponse safely extracts the text content from a Gemini response.
func extractTextResponse(resp *genai.GenerateContentResponse) string {
    var textContent string
    if resp != nil && len(resp.Candidates) > 0 && resp.Candidates[0].Content != nil {
        for _, part := range resp.Candidates[0].Content.Parts {
            if txt, ok := part.(genai.Text); ok {
                textContent += string(txt)
            }
        }
    }
    return textContent
}