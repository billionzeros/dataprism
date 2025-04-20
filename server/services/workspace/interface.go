package workspaceService

import "github.com/OmGuptaIND/shooting-star/db/models"

type WorkspaceService interface {
	// CreateWorkspace creates a new workspace in the database.
	CreateWorkspace(workspace *models.Workspace) (*models.Workspace, error)

	// GetWorkspaceById retrieves a workspace by its ID from the database.
	GetWorkspaceById(id string) (*models.Workspace, error)

	// GetWorkspaceByName retrieves a workspace by its name from the database.
	GetWorkspaceByName(name string) (*models.Workspace, error)

	// GetAllWorkspaces retrieves all workspaces from the database.
	GetAllWorkspaces() ([]models.Workspace, error)

	// Close closes the workspace service and releases any resources.
	Close()
}