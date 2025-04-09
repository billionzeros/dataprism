package blocks

import "github.com/OmGuptaIND/shooting-star/db/models"

// BlockService is an interface that defines the methods for block-related operations.
type BlockService interface {
	// CreateBlock creates a new block in the database.
	CreateBlock(block *models.Block) (*models.Block, error)

	// UpdateBlock updates an existing block in the database.
	UpdateBlock(block *models.Block) (*models.Block, error)

	// DeleteBlock deletes a block from the database.
	DeleteBlock(id string) error

	// GetBlockByID retrieves a block by its ID from the database.
	GetBlockByID(id string) (*models.Block, error)

	// GetBlockByDocumentID retrieves a block by its document ID from the database.
	GetBlockByDocumentID(documentId string) ([]*models.Block, error)
}