package documents

import "github.com/OmGuptaIND/shooting-star/db/models"


type DocumentService interface {
	// CreateDocument creates a new document in the database.
	CreateDocument(document *models.Document) (*models.Document, error)

	// GetDocumentByID retrieves a document by its ID from the database.
	GetDocumentByID(id string) (*models.Document, error)

	// DeleteDocument deletes a document from the database.
	DeleteDocument(id string) error

	// GetDocumentByTitle retrieves a document by its title from the database.
	GetDocumentByTitle(title string) (*models.Document, error)

	// GetAllDocuments retrieves all documents from the database.
	GetAllDocuments() ([]*models.Document, error)
}