package tools

import "github.com/google/generative-ai-go/genai"

type ToolType string


// Define the schema for the search_relevant_documents tool
const SearchRelevantDocumentsToolType ToolType = "search_relevant_documents"

var SearchRelevantDocumentsTool = &genai.Tool{
    FunctionDeclarations: []*genai.FunctionDeclaration{{
        Name:        string(SearchRelevantDocumentsToolType),
        
        Description: `Search for relevant document columns or content based on the user's question and conversation history, 
        Send a Query Text Parameter (query_text) for which an cosine similarity search will be performed, which will result in relevant columns and details of documents,
        which must be used or is relevant to the user's question and conversation history.

        Example:
        {
            "query_text": "What is the capital of France?"
        }

        The above query will search for relevant document columns or content based on the user's question and conversation history,
        which will result in relevant columns and details of documents.
        The response will include the relevant document columns and their details.
        `,

        Parameters: &genai.Schema{
            Type: genai.TypeObject,
            Properties: map[string]*genai.Schema{
                "query_text": {
                    Type:        genai.TypeString,
                    Description: "The specific text query to use for searching relevant document columns or content based on the user's question and conversation history, for which a embedding search using the cosine similarity will be performed.",
                },
            },
            Required: []string{"query_text"},
        },
    }},
}

// Execute_data_query tool
const ExecuteCSVQueryToolType ToolType = "execute_csv_query"

var ExecuteCSVQueryTool = &genai.Tool{
    FunctionDeclarations: []*genai.FunctionDeclaration{{
        Name:        "execute_csv_query",
        Description: "Executes a query (e.g., SQL-like) against the actual data in specified CSV uploads to retrieve specific values, filter data, or perform calculations needed to answer the user's question, based on the relevant document columns and their details.",
        Parameters: &genai.Schema{
            Type: genai.TypeObject,
            Properties: map[string]*genai.Schema{
                "query_string": {
                    Type:        genai.TypeString,
                    Description: "The query to execute. Use standard SQL syntax where possible, referencing columns by their exact names (e.g., 'SELECT seller_state, COUNT(*) FROM data GROUP BY seller_state ORDER BY COUNT(*) DESC LIMIT 5').",
                },
                "upload_ids": {
                    Type: genai.TypeArray,
                    Items: &genai.Schema{
                        Type: genai.TypeString,
                    },
                    Description: "Optional: List of specific upload IDs (found via 'search_relevant_documents') to query. If relevant IDs were found previously, include them.",
                },
            },
            Required: []string{"query_string"},
        },
    }},
}