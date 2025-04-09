package schema

type DocumentType string

// ---- UploadDocument ---
type UploadCsvRequest struct {
	// Name of the Document being uploaded
	FileName string `json:"file_name" validate:"required"`

	// Description of the Document being uploaded
	Description string `json:"description" validate:"required"`
}

type UploadDocumentResponse struct {
	// VectorID is the ID of the vector created in the database
	VectorID string `json:"vector_id"`

	// TokenUsed is the number of tokens used for the Document Processing
	TokenUsed int64 `json:"token_used"`
}