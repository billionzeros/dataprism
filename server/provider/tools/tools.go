package tools

import "github.com/google/generative-ai-go/genai"

// Define the schema for the search_relevant_documents tool
var SearchRelevantDocumentsTool = &genai.Tool{
    FunctionDeclarations: []*genai.FunctionDeclaration{{
        Name:        string(SearchRelevantDocumentsToolType),
        
        Description: `Search for relevant document columns or content based on the user's question and conversation history, 
        Send a Query Text Parameter (query_text) for which an cosine similarity search will be performed, which will result in relevant columns and details of documents.
        
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