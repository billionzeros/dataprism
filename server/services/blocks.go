package services

import (
	"github.com/OmGuptaIND/shooting-star/db"
	"github.com/OmGuptaIND/shooting-star/db/models"
	"go.uber.org/zap"
)


type blockService struct {
	logger *zap.Logger
}

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


// BlockService defines the interface for block-related operations.
func NewBlockService(logger *zap.Logger) BlockService {
	return &blockService{
		logger: logger,
	}
}

// CreateBlock creates a new block in the database.
func (s *blockService) CreateBlock(block *models.Block) (*models.Block, error) {
	s.logger.Info("Creating block", zap.String("title", string(block.Type)))

	result := db.Conn.Create(block)
	if result.Error != nil {
		return block, result.Error
	}

	return block, nil
}

// UpdateBlock updates an existing block in the database.
func (s *blockService) UpdateBlock(block *models.Block) (*models.Block, error) {
	s.logger.Info("Updating block", zap.String("title", string(block.Type)))

	result := db.Conn.Save(block)
	if result.Error != nil {
		return block, result.Error
	}

	return block, nil
}

// DeleteBlock deletes a block from the database.
func (s *blockService) DeleteBlock(id string) error {
	s.logger.Info("Deleting block", zap.String("id", id))

	result := db.Conn.Where("id = ?", id).UpdateColumn("deleted_at", nil)
	if result.Error != nil {
		return result.Error
	}

	return nil
}

// GetBlockByID retrieves a block by its ID from the database.
func (s *blockService) GetBlockByID(id string) (*models.Block, error) {
	s.logger.Info("Retrieving block by ID", zap.String("id", id))

	block := &models.Block{}
	result := db.Conn.Where("id = ?", id).First(block)
	if result.Error != nil {
		return nil, result.Error
	}

	return block, nil
}

// GetBlockByDocumentID retrieves a block by its document ID from the database.
func (s *blockService) GetBlockByDocumentID(documentId string) ([]*models.Block, error) {
	s.logger.Info("Retrieving block by document ID", zap.String("documentId", documentId))

	var blocks []*models.Block
	result := db.Conn.Where("document_id = ?", documentId).Find(&blocks)
	if result.Error != nil {
		return nil, result.Error
	}

	return blocks, nil
}

