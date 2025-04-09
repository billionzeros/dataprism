package handlers

import (
	"time"

	"github.com/OmGuptaIND/shooting-star/db"
	"github.com/OmGuptaIND/shooting-star/db/models"
)

// CreateBlock handles the creation of a block, based on the provided block model.
func CreateBlock(block *models.Block) (*models.Block, error) {
	result := db.Conn.Create(block)
	if result.Error != nil {
		return block, result.Error
	}

	return block, nil
}

// UpdateBlock updates an existing block in the database.
func UpdateBlock(block *models.Block) (*models.Block, error) {
	result := db.Conn.Save(block)
	if result.Error != nil {
		return block, result.Error
	}

	return block, nil
}

// DeleteBlock deletes a block from the database.
func DeleteBlock(id string) error {
	result := db.Conn.Where("id = ?", id).UpdateColumn("deleted_at", time.Now())
	if result.Error != nil {
		return result.Error
	}

	return nil
}

// GetBlockByID retrieves a block by its ID from the database.
func GetBlockByID(id string) (*models.Block, error) {
	block := &models.Block{}
	result := db.Conn.Where("id = ?", id).First(block)
	if result.Error != nil {
		return nil, result.Error
	}

	return block, nil
}