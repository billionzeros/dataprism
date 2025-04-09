package schema

import "github.com/OmGuptaIND/shooting-star/db/models"

// ---- CreateDocument ---
type CreateDocumentRequest struct {
	Title string `json:"title" validate:"required,min=1,max=255" message:"Title must be between 1 and 255 characters long"`
}

type CreateDocumentResponse struct {
	DocumentID string `json:"document_id"`

	*models.Document
}

// ----------------------


// ---- GetDocumentByID ---
type GetDocumentByIDRequest struct {
	ID string `json:"id" validate:"required"`
}

type GetDocumentByIDResponse struct {
	DocumentID string `json:"document_id"`
	Title       string `json:"title"`
}

// ----------------------

// ---- DeleteDocument ---
type DeleteDocumentRequest struct {
	ID string `json:"id" validate:"required"`
}

type DeleteDocumentResponse struct {
	Message string `json:"message"`
}

// ----------------------