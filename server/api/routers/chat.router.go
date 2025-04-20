package routers

import (
	"context"
	"fmt"
	"time"

	"github.com/OmGuptaIND/shooting-star/api/responses"
	"github.com/OmGuptaIND/shooting-star/appError"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	chatService "github.com/OmGuptaIND/shooting-star/services/chat"
	"github.com/gofiber/fiber/v3"
	"go.uber.org/zap"
)

// DocumentRouter handles the routing for document-related endpoints.
type ChatRouter struct {
	ctx context.Context

	// chatService is the service used for chat-related operations.
	chatServices map[string]chatService.ChatService

	logger *zap.Logger
}

// NewDocumentRouter creates a new DocumentRouter instance with the provided fiber.Router.
func RegisterChatRoutes(ctx context.Context, baseRouter fiber.Router) {
	handler := &ChatRouter{
		ctx: ctx,
		chatServices: make(map[string]chatService.ChatService),
		logger: logger.FromCtx(ctx),
	}

	// Grouping the routes under `/chat`
	chatGroup := baseRouter.Group("/chat")

	chatGroup.Post("/new", handler.newChat)
	chatGroup.Post("/push", handler.pushChat)
}

// newChat handles the creation of a new chat.
func (cr *ChatRouter) newChat(c fiber.Ctx) error {
	req := new(chatService.CreateNewChat)

	if err := c.Bind().Body(&req); err != nil {
		return responses.BadRequest(c, appError.InternalError, "Invalid request body")
	}

	if req.DocumentID == "" || req.BlockId == "" {
		return responses.BadRequest(c, appError.InternalError, "Document ID and block ID are required")
	}

	cr.logger.Info("Received new chat request", zap.String("documentID", req.DocumentID), zap.String("blockId", req.BlockId))

	newChatId := fmt.Sprintf("%s-%s", req.DocumentID, req.BlockId)

	// Create a new chat service instance
	service, err := chatService.NewChatService(cr.ctx, req.DocumentID, newChatId)
	if err != nil {
		cr.logger.Error("Error creating chat service", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, "Failed to create chat service")
	}

	// Store the chat service instance in the map
	cr.chatServices[newChatId] = service
	cr.logger.Info("Chat service created successfully", zap.String("chatId", newChatId))

	return responses.OK(c, map[string]string{"chatId": newChatId})
}

// pushChat handles the pushing of a new user chat message.
func (cr *ChatRouter) pushChat(c fiber.Ctx) error {
	req := new(chatService.ChatMessage)

	if err := c.Bind().Body(&req); err != nil {
		return responses.BadRequest(c, appError.InternalError, "Invalid request body")
	}

	if req.DocumentID == "" || req.Message == "" {
		cr.logger.Error("Invalid request parameters", zap.String("documentID", req.DocumentID), zap.String("message", req.Message))
		return responses.BadRequest(c, appError.InternalError, "Document ID and message are required")
	}

	cr.logger.Info("Received document creation request", zap.String("documentID", req.DocumentID), zap.String("message", req.Message))

	service, ok := cr.chatServices[req.DocumentID]
	if !ok {
		cr.logger.Error("Chat service not found", zap.String("documentID", req.DocumentID))
		return responses.BadRequest(c, appError.InternalError, "Chat service not found")
	}

	newUserMessage := &chatService.ChatMessage{
		DocumentID: req.DocumentID,
		Message: req.Message,
		Role: chatService.UserRole,
		Timestamp: time.Now().Format(time.RFC3339),
	}

	assistantResponse, err := service.PushNewChat(newUserMessage); 
	if err != nil {
		cr.logger.Error("Error adding new message", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, "Failed to add new message")
	}

	return responses.OK(c, assistantResponse)
}