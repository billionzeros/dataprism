package workspaceService

import (
	"context"

	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/db"
	"github.com/OmGuptaIND/shooting-star/db/models"
	"github.com/google/generative-ai-go/genai"
	"go.uber.org/zap"
)

// WorkspaceService defines the interface for document-related operations.
type service struct {
	ctx context.Context

	// GenerativeModel is the generative model used for chat interactions.
	generativeModel *genai.GenerativeModel

	// Logger is the logger instance for logging messages.
	logger *zap.Logger
}

// New creates a new instance of WorkspaceService with the provided logger.
func New(ctx context.Context) (WorkspaceService) {
	l := logger.FromCtx(ctx).With(zap.String("service", "workspaceService"))

	workspaceService := &service{
		ctx: ctx,
		logger: l,
	}

	return workspaceService
}

// CreateWorkspace creates a new workspace in the database.
func (s *service) CreateWorkspace(workspace *models.Workspace) (*models.Workspace, error) {
	s.logger.Info("Creating new workspace", zap.String("name", workspace.Name))

	result := db.Conn.Create(workspace)
	if result.Error != nil {
		return workspace, result.Error
	}

	return workspace, nil
}

