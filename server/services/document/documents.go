package documentservice

import (
	"context"

	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/db"
	"github.com/OmGuptaIND/shooting-star/db/models"
	"go.uber.org/zap"
)

type documentService struct {
	ctx context.Context
	logger *zap.Logger
}



// Creates a new instance of DocumentService with the provided logger.
func New(ctx context.Context) DocumentService {
	return &documentService{
		ctx: ctx,
		logger: logger.FromCtx(ctx),
	}
}

// CreateDocument creates a new document in the database.
func (s *documentService) CreateDocument(document *models.Document) (*models.Document, error) {
	result := db.Conn.Create(document)
	if result.Error != nil {
		return document, result.Error
	}

	return document, nil
}

// GetDocumentByID retrieves a document by its ID from the database.
func (s *documentService) GetDocumentByID(id string) (*models.Document, error) {
	s.logger.Info("Retrieving document by ID", zap.String("id", id))

	document := &models.Document{}
	result := db.Conn.Where("id = ?", id).First(document)
	if result.Error != nil {
		return nil, result.Error
	}

	return document, nil
}

// DeleteDocument deletes a document from the database.
func (s *documentService) DeleteDocument(id string) error {
	s.logger.Info("Deleting document", zap.String("id", id))

	document := &models.Document{}
	result := db.Conn.Where("id = ?", id).Delete(document)
	if result.Error != nil {
		return result.Error
	}

	return nil
}

// GetDocumentByTitle retrieves a document by its title from the database.
func (s *documentService) GetDocumentByTitle(title string) (*models.Document, error) {
	s.logger.Info("Retrieving document by title", zap.String("title", title))

	document := &models.Document{}
	result := db.Conn.Where("title = ?", title).First(document)
	if result.Error != nil {
		return nil, result.Error
	}

	return document, nil
}

// GetAllDocuments retrieves all documents from the database.
func (s *documentService) GetAllDocuments() ([]*models.Document, error) {
	s.logger.Info("Retrieving all documents")

	documents := []*models.Document{}
	result := db.Conn.Find(&documents)
	if result.Error != nil {
		return nil, result.Error
	}

	return documents, nil
}