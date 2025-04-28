package schema


type DocumentType string

// ---- UploadDocument ---
type UploadCsvRequest struct {
	// Name of the Document being uploaded
	FileName string `json:"file_name" validate:"required"`

	// Path to the Document being uploaded
	FilePath string `json:"file_path" validate:"required"`

	// Description of the Document being uploaded
	Description string `json:"description" validate:"required"`

	// WorkspaceID is the ID of the workspace to which the document belongs
	WorkspaceID string `json:"workspace_id"`
}

type UploadCsvResponse struct {
	// UploadId is the ID of the upload
	Message string `json:"message"`
}
