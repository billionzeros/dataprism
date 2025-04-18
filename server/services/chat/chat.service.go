package chatservice

import (
	"context"
	"time"

	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/provider"
	"github.com/google/generative-ai-go/genai"
	"go.uber.org/zap"
)


type chatService struct {
	ctx context.Context

	// GenerativeModel is the generative model used for chat interactions.
	model *genai.GenerativeModel

	// ChatSession is the chat session for the current conversation.
	chatSession *genai.ChatSession

	// Logger is the logger instance for logging messages.
	logger *zap.Logger
}

// ChatService defines the interface for chat-related operations.
type ChatService interface {
	// AddMessage adds a new message to the chat.
	AddNewMessage(message *ChatMessage) error
}


// NewDocumentService creates a new instance of DocumentService with the provided logger.
func NewChatService(ctx context.Context, documentId string, chatId string) (ChatService, error) {
	gemini, err := provider.NewGeminiProvider(ctx)
	if err != nil {
		return nil, err
	}
	
	model := gemini.GenerativeModel(string(provider.Gemini2_0Flash))

	model.SystemInstruction = &genai.Content{
		Parts: []genai.Part{genai.Text(`
			You are a helpful assistant. You will be provided with a document ID and a chat ID. 
			Your task is to assist the user in querying the document and provide relevant information based on the chat context. Please ensure that you maintain the context of the conversation and provide accurate responses.
			
			Based on the Query, you will be tasked to do relevant tool calls 
		`)},
	}

	model.ResponseMIMEType = "application/json"

	// Create a new chat session
	chatSession := model.StartChat()

	return &chatService{
		ctx: ctx,
		model: model,
		chatSession: chatSession,
		logger: logger.FromCtx(ctx),
	}, nil
}

// AddNewMessage adds a new message to the chat.
func (c *chatService) AddNewMessage(chat *ChatMessage) error {
	c.logger.Info("Adding new message to chat", zap.String("message", chat.Message), zap.String("role", string(chat.Role)))

	ctx, cancel := context.WithTimeout(c.ctx, 20*time.Second)
	defer cancel()

	// Add the message to the chat session
	resp, err := c.chatSession.SendMessage(ctx, genai.Text(chat.Message))
	if err != nil {
		c.logger.Error("Error sending message", zap.Error(err))
		return err
	}

	c.logger.Sugar().Info("Message Response", resp)

	return nil
}