package handlers

import (
	"github.com/OmGuptaIND/shooting-star/db"
	"github.com/OmGuptaIND/shooting-star/db/models"
)

// CreateDocument handles the creation of a document, based on the provided document model.
func CreateDocument(document *models.Document) (*models.Document, error) {
	result := db.Conn.Create(document)
	if result.Error != nil {
		return document, result.Error
	}

	return document, nil
}

// UpdateDocument updates an existing document in the database.
func GetDocumentByID(id string) (*models.Document, error) {
	document := &models.Document{}
	result := db.Conn.Where("id = ?", id).First(document)
	if result.Error != nil {
		return nil, result.Error
	}

	return document, nil
}

// DeleteDocument deletes a document from the database.
func DeleteDocument(id string) error {
	document := &models.Document{}
	result := db.Conn.Where("id = ?", id).Delete(document)
	if result.Error != nil {
		return result.Error
	}

	return nil
}

// GetDocumentByName retrieves a document by its name from the database.
func GetDocumentByTitle(title string) (*models.Document, error) {
	document := &models.Document{}
	result := db.Conn.Where("title = ?", title).First(document)
	if result.Error != nil {
		return nil, result.Error
	}

	return document, nil
}

// GetAllDocuments retrieves all documents from the database.
func GetAllDocuments() ([]*models.Document, error) {
	documents := []*models.Document{}
	result := db.Conn.Find(&documents)
	if result.Error != nil {
		return nil, result.Error
	}

	return documents, nil
}