package schema

import "github.com/OmGuptaIND/shooting-star/db/models"

// ---- CreateDocument ---
type CreateWorkspaceRequest struct {
	Name string `json:"name" validate:"required,min=1,max=255" message:"Name must be between 1 and 255 characters long"`
	
	Description string `json:"description" validate:"required,min=1,max=255" message:"Description must be between 1 and 255 characters long"`
}

type CreateWorkspaceResponse struct {
	WorkspaceId string `json:"workspace_id"`

	*models.Workspace
}

// ----------------------

type GetWorkspaceByNameRequest struct {
	Name string `json:"name" validate:"required,min=1,max=255" message:"Name must be between 1 and 255 characters long"`
}

type GetWorkspaceByNameResponse struct {
	WorkspaceId string `json:"workspace_id"`

	*models.Workspace
}

// ----------------------

type GetWorkspaceByIdRequest struct {
	WorkspaceId string `json:"workspace_id" validate:"required,min=1,max=255" message:"Workspace ID must be between 1 and 255 characters long"`
}

type GetWorkspaceByIdResponse struct {
	WorkspaceId string `json:"workspace_id"`

	*models.Workspace
}

// ----------------------

type GetAllWorkspacesResponse struct {
	Workspaces []models.Workspace `json:"workspaces"`
}

// ----------------------