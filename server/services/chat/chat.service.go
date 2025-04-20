package chatService

import (
	"context"
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

	// DocumentId is the ID of the document being Queried.
	documentId string

	// Logger is the logger instance for logging messages.
	logger *zap.Logger
}

// ChatService defines the interface for chat-related operations.
type ChatService interface {
	// Push a new message to the chat.
	PushNewChat(message *ChatMessage) (*ChatMessage, error)
}


// NewDocumentService creates a new instance of DocumentService with the provided logger.
func NewChatService(ctx context.Context, documentId string, chatId string) (ChatService, error) {
	gemini, err := provider.NewGeminiProvider(ctx)
	if err != nil {
		return nil, err
	}
	
	gm := gemini.GenerativeModel(string(provider.Gemini2_0Flash))

	gm.Tools = []*genai.Tool{
		tools.SearchRelevantDocumentsTool,
	}

	em := gemini.EmbeddingModel(string(provider.Embedding001))

	gm.SystemInstruction = &genai.Content{
        Parts: []genai.Part{genai.Text(fmt.Sprintf(`
            You are a helpful assistant specializing in analyzing data from uploaded CSV files.
            You are currently assisting with document ID: %s.

            When the user asks a question that requires looking up information in the CSV data, use the 'search_relevant_documents' tool to find relevant columns or data points.
            Generate the 'query_text' argument for the tool based on the user's specific question and the conversation context.
            
			After receiving the search results from the tool, synthesize a helpful and informative answer for the user based *only* on the provided search results and the conversation history.
            Do not invent information not present in the search results. If the search results are empty or don't contain the answer, state that clearly.
        `, documentId))},
    }

	chatSession := gm.StartChat()

	return &chatService{
		ctx: ctx,
		documentId: documentId,
		generativeModel: gm,
		embeddingModel: em,
		chatSession: chatSession,
		logger: logger.FromCtx(ctx),
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

	if len(resp.Candidates) > 0 && resp.Candidates[0].Content != nil {
		part := resp.Candidates[0].Content.Parts[0]

		if fc, ok := part.(*genai.FunctionCall); ok {
			c.logger.Info("Function call detected", zap.String("function_name", fc.Name))
			
			if err := c.handleFunctionCall(fc); err != nil {
				c.logger.Error("Error handling function call", zap.Error(err))
				return nil, appError.New(appError.InternalError, err.Error(), err)
			}
		}
	}

	assistantResponse := extractTextResponse(resp)
	if assistantResponse == "" {
        c.logger.Warn("LLM response was empty or contained no text part after potential function call")
        assistantResponse = "I received a response, but it contained no text content." // Default message
    }

	responseMessage := &ChatMessage{
		DocumentID: c.documentId,
		MessageId: chat.MessageId,
		Message: assistantResponse,
		Role: AssistantRole,
		Timestamp: time.Now().Format(time.RFC3339),
	}

	return responseMessage, nil
}

// handleFunctionCall handles the function call and executes the appropriate logic.
func (c *chatService) handleFunctionCall(fc *genai.FunctionCall) (error) {
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
	_, err = c.chatSession.SendMessage(c.ctx, funcResp)
	if err != nil {
		c.logger.Error("Error sending function call response", zap.Error(err))
		return appError.New(appError.InternalError, err.Error(), err)
	}

	c.logger.Info("Function call response sent", zap.String("function_name", fc.Name))

	return err
}

// handleSearchRelevantDocuments executes the actual search logic.
func (c *chatService) handleSearchRelevantDocuments(fc *genai.FunctionCall) (*genai.FunctionResponse, error) {
    queryText, ok := fc.Args["query_text"].(string)
    if !ok || queryText == "" {
        return nil, fmt.Errorf("missing or invalid 'query_text' argument")
    }

    c.logger.Info("Executing search_relevant_documents", zap.String("query_text", queryText))

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
                        Where("source_identifier = ?", c.documentId).
                        Where("source_type = ?", models.EmbeddingSourceTypeCSVColumn).
                        Order("similarity DESC").
                        Limit(limit).
                        Find(&results).Error
    if err != nil {
        return nil, fmt.Errorf("database search failed: %w", err)
    }

    formattedResults := make([]map[string]interface{}, 0, len(results))
    for _, res := range results {
        formattedResults = append(formattedResults, map[string]interface{}{
            "column_name": res.ColumnOrChunkName,
            "content_snippet": res.OriginalText,
            "relevance_score": res.Similarity,
        })
    }

    c.logger.Info("Search results found", zap.Int("count", len(formattedResults)))

    return &genai.FunctionResponse{
        Name: fc.Name,
        Response: map[string]interface{}{
            "search_results": formattedResults,
        },
    }, nil
}

// ExecuteFunctionCall executes a function call based on the provided function call object.
func (c *chatService) executeFunctionCall(fc *genai.FunctionCall) (*genai.FunctionResponse, error) {
	switch fc.Name {
		case string(tools.SearchRelevantDocumentsToolType):
			return c.handleSearchRelevantDocuments(fc)
		
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