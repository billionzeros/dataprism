package workspaceService

import (
	"context"

	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/db"
	"github.com/OmGuptaIND/shooting-star/db/models"
	"go.uber.org/zap"
)

// WorkspaceService defines the interface for document-related operations.
type service struct {
	ctx context.Context

	cancelFunc context.CancelFunc

	// Logger is the logger instance for logging messages.
	logger *zap.Logger
}

// New creates a new instance of WorkspaceService with the provided logger.
func New(ctx context.Context) (WorkspaceService) {
	l := logger.FromCtx(ctx).With(zap.String("service", "workspaceService"))

	ctx, cancelFunc := context.WithCancel(ctx)

	workspaceService := &service{
		ctx: ctx,
		cancelFunc: cancelFunc,

		logger: l,
	}

	return workspaceService
}

// Close closes the workspace service and releases any resources.
func (s *service) Close() {
	s.logger.Info("Closing workspace service")
	s.cancelFunc()
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

// GetWorkspaceById retrieves a workspace by its ID from the database.
func (s *service) GetWorkspaceById(id string) (*models.Workspace, error) {
	s.logger.Info("Fetching workspace by ID", zap.String("id", id))

	var workspace models.Workspace
	result := db.Conn.Where("id = ?", id).First(&workspace)
	if result.Error != nil {
		return nil, result.Error
	}

	return &workspace, nil
}

// GetWorkspaceByName retrieves a workspace by its name from the database.
func (s *service) GetWorkspaceByName(name string) (*models.Workspace, error) {
	s.logger.Info("Fetching workspace by name", zap.String("name", name))

	var workspace models.Workspace
	result := db.Conn.Where("name = ?", name).First(&workspace)
	if result.Error != nil {
		return nil, result.Error
	}

	return &workspace, nil
}

// GetAllWorkspaces retrieves all workspaces from the database.
func (s *service) GetAllWorkspaces() ([]models.Workspace, error) {
	s.logger.Info("Fetching all workspaces")

	var workspaces []models.Workspace
	result := db.Conn.Find(&workspaces)
	if result.Error != nil {
		return nil, result.Error
	}

	return workspaces, nil
}
