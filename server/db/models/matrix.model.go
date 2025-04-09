package models

import (
	"errors"
	"time"

	"gorm.io/gorm"
)

// BlockMatrix is the struct representing a matrix of Blocks and the relationships between them
type BlockMatrix struct {
    // Primary key for the matrix entry itself
    ID string `gorm:"primaryKey;type:uuid;default:gen_random_uuid()"`

    DocumentID string `gorm:"type:uuid;not null;uniqueIndex:idx_doc_block;index;constraint:OnDelete:CASCADE"`

    BlockID     string `gorm:"type:uuid;not null;uniqueIndex:idx_doc_block;index;constraint:OnDelete:CASCADE"`

    IsRoot       bool    `gorm:"default:false;index"`
    NextBlockID   *string `gorm:"type:uuid;index;constraint:OnDelete:SET NULL"`
    PrevBlockID   *string `gorm:"type:uuid;index;constraint:OnDelete:SET NULL"`
    ParentBlockID *string `gorm:"type:uuid;index;constraint:OnDelete:SET NULL"`
    Level       int     `gorm:"type:int;not null;default:0"`

    CreatedAt time.Time

    // Foreign key references BlockID field in this struct to the PK of Block struct
    Block        *Block         `gorm:"foreignKey:BlockID"`
}


// BeforeCreate hook to ensure proper block linking
func (bs *BlockMatrix) BeforeCreate(tx *gorm.DB) error {
	if bs.IsRoot {
		var count int64
		tx.Model(&BlockMatrix{}).Where("document_id = ? AND is_root = ?", bs.DocumentID, true).Count(&count)
		if count > 0 {
			tx.Model(&BlockMatrix{}).Where("document_id = ? AND is_root = ?", bs.DocumentID, true).UpdateColumn("is_root", false)
		}
		
		tx.Model(&Document{}).Where("id = ?", bs.DocumentID).UpdateColumn("root_block_id", bs.BlockID)
	}
	
	if bs.NextBlockID != nil {
		var nextBlockMatrix BlockMatrix
		if err := tx.Where("block_id = ?", *bs.NextBlockID).First(&nextBlockMatrix).Error; err == nil {
			if errors.Is(err, gorm.ErrRecordNotFound) {
                return errors.New("specified next block not found in the same document matrix")
            }

			if nextBlockMatrix.DocumentID != bs.DocumentID {
				return errors.New("next block must be in the same document")
			}

			tx.Model(&BlockMatrix{}).Where("block_id = ?", *bs.NextBlockID).Update("prev_block_id", bs.BlockID)
		}
	}
	
	if bs.PrevBlockID != nil {
		var prevBlockMatrix BlockMatrix
		if err := tx.Where("block_id = ?", *bs.PrevBlockID).First(&prevBlockMatrix).Error; err == nil {
			if errors.Is(err, gorm.ErrRecordNotFound) {
                return errors.New("specified previous block not found in the same document matrix")
			}
			
			if prevBlockMatrix.DocumentID != bs.DocumentID {
				return errors.New("previous block must be in the same document")
			}
			tx.Model(&BlockMatrix{}).Where("block_id = ?", *bs.PrevBlockID).Update("next_block_id", bs.BlockID)
		}
	}
	
	return nil
}


// AfterDelete hook to ensure proper block relinking after deletion
func (bs *BlockMatrix) AfterDelete(tx *gorm.DB) error {
	if bs.NextBlockID != nil && bs.PrevBlockID != nil {
		tx.Model(&BlockMatrix{}).Where("block_id = ?", *bs.NextBlockID).Update("prev_block_id", bs.PrevBlockID)
		tx.Model(&BlockMatrix{}).Where("block_id = ?", *bs.PrevBlockID).Update("next_block_id", bs.NextBlockID)
	} else if bs.NextBlockID != nil {
		tx.Model(&BlockMatrix{}).Where("block_id = ?", *bs.NextBlockID).Update("prev_block_id", nil)
		
		if bs.IsRoot {
			tx.Model(&BlockMatrix{}).Where("block_id = ?", *bs.NextBlockID).Update("is_root", true)
			tx.Model(&Document{}).Where("id = ?", bs.DocumentID).Update("root_block_id", *bs.NextBlockID)
		}
	} else if bs.PrevBlockID != nil {
		tx.Model(&BlockMatrix{}).Where("block_id = ?", *bs.PrevBlockID).Update("next_block_id", nil)
	}
	
	if bs.IsRoot {
		var count int64
		tx.Model(&BlockMatrix{}).Where("document_id = ?", bs.DocumentID).Count(&count)
		
		if count == 0 {
			tx.Model(&Document{}).Where("id = ?", bs.DocumentID).Update("root_block_id", nil)
		}
	}
	
	return nil
}

func (BlockMatrix) TableName() string {
    return "block_matrix"
}

