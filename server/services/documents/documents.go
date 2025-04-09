package documents

import (
	"context"

	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/db"
	"github.com/OmGuptaIND/shooting-star/db/models"
	"go.uber.org/zap"
)

type service struct {
	ctx context.Context
	logger *zap.Logger
}

// NewDocumentService creates a new instance of DocumentService with the provided logger.
func NewDocumentService(ctx context.Context) DocumentService {
	return &service{
		ctx: ctx,
		logger: logger.FromCtx(ctx),
	}
}

// CreateDocument creates a new document in the database.
func (s *service) CreateDocument(document *models.Document) (*models.Document, error) {
	result := db.Conn.Create(document)
	if result.Error != nil {
		return document, result.Error
	}

	return document, nil
}

// GetDocumentByID retrieves a document by its ID from the database.
func (s *service) GetDocumentByID(id string) (*models.Document, error) {
	s.logger.Info("Retrieving document by ID", zap.String("id", id))

	document := &models.Document{}
	result := db.Conn.Where("id = ?", id).First(document)
	if result.Error != nil {
		return nil, result.Error
	}

	return document, nil
}

// DeleteDocument deletes a document from the database.
func (s *service) DeleteDocument(id string) error {
	s.logger.Info("Deleting document", zap.String("id", id))

	document := &models.Document{}
	result := db.Conn.Where("id = ?", id).Delete(document)
	if result.Error != nil {
		return result.Error
	}

	return nil
}

// GetDocumentByTitle retrieves a document by its title from the database.
func (s *service) GetDocumentByTitle(title string) (*models.Document, error) {
	s.logger.Info("Retrieving document by title", zap.String("title", title))

	document := &models.Document{}
	result := db.Conn.Where("title = ?", title).First(document)
	if result.Error != nil {
		return nil, result.Error
	}

	return document, nil
}

// GetAllDocuments retrieves all documents from the database.
func (s *service) GetAllDocuments() ([]*models.Document, error) {
	s.logger.Info("Retrieving all documents")

	documents := []*models.Document{}
	result := db.Conn.Find(&documents)
	if result.Error != nil {
		return nil, result.Error
	}

	return documents, nil
}