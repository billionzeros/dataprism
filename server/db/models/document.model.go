package models

import (
	"time"

	"gorm.io/gorm"
)

// Document represents a collection of blocks
type Document struct {
	ID        string    `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`

	// Document metadata
	Title     string    `json:"title"`
	RootBlockID *string  `gorm:"type:uuid;index;constraint:OnDelete:SET NULL"`
	CreatedAt time.Time `json:"createdAt"`
	UpdatedAt time.Time `json:"updatedAt"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
	
	// Virtual field - not stored in database
	Blocks []Block `gorm:"-" json:"blocks,omitempty"`
	BlockMatrix   []BlockMatrix `gorm:"-" json:"blockMatrix,omitempty"`
}