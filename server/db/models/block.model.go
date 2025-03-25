package models

import (
	"encoding/json"
	"errors"
	"time"

	"gorm.io/gorm"
)

type BlockType string

const (
	// Block types
	HeadingBlock BlockType = "heading"
	ParagraphBlock    BlockType = "paragraph"
	ListBlock    BlockType = "list"
	QuoteBlock   BlockType = "quote"
	CodeBlock    BlockType = "code"
	EmbedBlock   BlockType = "embed"
	ImageBlock   BlockType = "image"
	TableBlock   BlockType = "table"
	LineChartBlock BlockType = "line-chart"
	BarChartBlock BlockType = "bar-chart"
	PieChartBlock BlockType = "pie-chart"
	ScatterChartBlock BlockType = "scatter-chart"
)

// This is used to store the content of a block in a JSONB column
type Block struct {
	ID string `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`

	// Document relationship - every block must belong to a document
	DocumentID string `gorm:"type:uuid;not null;index" json:"documentId"`
	
	// Block relationships
	IsRoot        bool   `gorm:"default:false" json:"isRoot"`
	NextBlockID   *string `gorm:"type:uuid;index" json:"nextBlockId"`
	PrevBlockID   *string `gorm:"type:uuid;index" json:"prevBlockId"`
	ParentBlockID *string `gorm:"type:uuid;index" json:"parentBlockId"`
	ParentBlockIndex *int  `json:"parentBlockIndex"`
	
	// Block type and content
	Type    BlockType       `gorm:"type:varchar(255);not null" json:"type"`
	Content BlockContentJSON `gorm:"type:jsonb;not null" json:"content"`
	
	// Standard timestamps
	CreatedAt time.Time      `json:"createdAt"`
	UpdatedAt time.Time      `json:"updatedAt"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

// BlockContentJSON is a type alias for a map of string to interface
type BlockContentJSON map[string]interface{}

// Implement the sql.Scanner interface for JSONB, which allows us to scan JSONB data from the database into a struct
func (bc *BlockContentJSON) Scan(value interface{}) error {
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("type assertion to []byte failed")
	}

	return json.Unmarshal(bytes, &bc)
}

// BeforeCreate hook to ensure proper block linking
// BeforeCreate hook to ensure proper block linking
func (b *Block) BeforeCreate(tx *gorm.DB) error {
	// Ensure the block is associated with a document
	if b.DocumentID == "" {
		return errors.New("block must belong to a document")
	}
	
	// If block is marked as root, ensure no other root exists in the same document
	if b.IsRoot {
		var count int64
		tx.Model(&Block{}).Where("document_id = ? AND is_root = ?", b.DocumentID, true).Count(&count)
		if count > 0 {
			// If there is already a root block in this document, unmark it			
			tx.Model(&Block{}).Where("document_id = ? AND is_root = ?", b.DocumentID, true).Update("is_root", false)
		}
		
		// Update the document to reference this block as root
		tx.Model(&Document{}).Where("id = ?", b.DocumentID).Update("root_block_id", b.ID)
	}
	
	// If this block has a next block, update that block's prev_block_id
	if b.NextBlockID != nil {
		// Ensure the next block is in the same document
		var nextBlock Block
		if err := tx.Where("id = ?", *b.NextBlockID).First(&nextBlock).Error; err == nil {
			if nextBlock.DocumentID != b.DocumentID {
				return errors.New("next block must be in the same document")
			}
		}
		
		tx.Model(&Block{}).Where("id = ?", *b.NextBlockID).Update("prev_block_id", b.ID)
	}
	
	// If this block has a prev block, update that block's next_block_id
	if b.PrevBlockID != nil {
		// Ensure the prev block is in the same document
		var prevBlock Block
		if err := tx.Where("id = ?", *b.PrevBlockID).First(&prevBlock).Error; err == nil {
			if prevBlock.DocumentID != b.DocumentID {
				return errors.New("previous block must be in the same document")
			}
		}
		
		tx.Model(&Block{}).Where("id = ?", *b.PrevBlockID).Update("next_block_id", b.ID)
	}
	
	// Ensure parent block is in the same document
	if b.ParentBlockID != nil {
		var parentBlock Block
		if err := tx.Where("id = ?", *b.ParentBlockID).First(&parentBlock).Error; err == nil {
			if parentBlock.DocumentID != b.DocumentID {
				return errors.New("parent block must be in the same document")
			}
		}
	}
	
	return nil
}


// AfterDelete hook to ensure proper block relinking after deletion
func (b *Block) AfterDelete(tx *gorm.DB) error {
	// If this block had a next and prev, link them together
	if b.NextBlockID != nil && b.PrevBlockID != nil {
		tx.Model(&Block{}).Where("id = ?", *b.NextBlockID).Update("prev_block_id", b.PrevBlockID)
		tx.Model(&Block{}).Where("id = ?", *b.PrevBlockID).Update("next_block_id", b.NextBlockID)
	} else if b.NextBlockID != nil {
		// If only next exists, update its prev to null
		tx.Model(&Block{}).Where("id = ?", *b.NextBlockID).Update("prev_block_id", nil)
		
		// If this was the root, make the next block the new root
		if b.IsRoot {
			// Update the next block to be the root
			tx.Model(&Block{}).Where("id = ?", *b.NextBlockID).Update("is_root", true)
			
			// Update the document to point to the new root
			tx.Model(&Document{}).Where("id = ?", b.DocumentID).Update("root_block_id", *b.NextBlockID)
		}
	} else if b.PrevBlockID != nil {
		// If only prev exists, update its next to null
		tx.Model(&Block{}).Where("id = ?", *b.PrevBlockID).Update("next_block_id", nil)
	}
	
	// If this was the only root block, update the document
	if b.IsRoot {
		// Check if this was the last block in the document
		var count int64
		tx.Model(&Block{}).Where("document_id = ?", b.DocumentID).Count(&count)
		
		if count == 0 {
			// Last block was deleted, clear the root_block_id in document
			tx.Model(&Document{}).Where("id = ?", b.DocumentID).Update("root_block_id", nil)
		}
	}
	
	return nil
}


// AfterCreate hook to update document's root_block_id if this is the first block
func (b *Block) AfterCreate(tx *gorm.DB) error {
	// If this is a root block, ensure the document points to it
	if b.IsRoot {
		return tx.Model(&Document{}).Where("id = ?", b.DocumentID).Update("root_block_id", b.ID).Error
	}
	
	// If document has no root_block_id, and this is the first block, make it the root
	var document Document
	if err := tx.Where("id = ?", b.DocumentID).First(&document).Error; err != nil {
		return err
	}
	
	if document.RootBlockID == nil {
		// Make this block the root
		b.IsRoot = true
		if err := tx.Model(b).Update("is_root", true).Error; err != nil {
			return err
		}
		
		// Update the document
		return tx.Model(&document).Update("root_block_id", b.ID).Error
	}
	
	return nil
}