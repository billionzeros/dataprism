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