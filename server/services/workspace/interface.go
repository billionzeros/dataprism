package workspaceService

import "github.com/OmGuptaIND/shooting-star/db/models"

type WorkspaceService interface {
	// CreateWorkspace creates a new workspace in the database.
	CreateWorkspace(workspace *models.Workspace) (*models.Workspace, error)
}