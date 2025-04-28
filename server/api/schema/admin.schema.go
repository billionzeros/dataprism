package schema

// ---- BuildMockDB ---
type BuildMockRequest struct {
	WorkspaceID string `json:"workspace_id"`
}

type BuildMockResponse struct {
	Message string `json:"message"`
	FilesQueued int    `json:"files_queued"`
	ErrorCount int    `json:"error_count"`
	ErrorDetails []string `json:"error_details"`
}

// ----------------------