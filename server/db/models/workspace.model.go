package models

import (
	"time"

	"gorm.io/gorm"
)

// Workspace represents a higher-level collection of documents
type Workspace struct {
	ID        string    `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`
	Name      string    `gorm:"type:text;not null"`
	Description string    `gorm:"type:text"`

	// Document metadata
	CreatedAt time.Time      `gorm:"not null;default:CURRENT_TIMESTAMP"`
    UpdatedAt time.Time      `gorm:"not null;default:CURRENT_TIMESTAMP"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`

	// Relationships
	Documents []Document `gorm:"foreignKey:WorkspaceID" json:"documents,omitempty"`

	// Define a relationship to the Uploads table
	WorkspaceUploads []WorkspaceUpload `gorm:"foreignKey:WorkspaceID" json:"workspace_uploads,omitempty"` // Has many links
}

func (Workspace) TableName() string {
    return "workspaces"
}