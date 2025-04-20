package models

import (
	"time"
)

type WorkspaceUpload struct {
	ID 		string `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`
    WorkspaceID string `gorm:"primaryKey;type:uuid"` // Part of the composite primary key
    UploadID    string `gorm:"primaryKey;type:uuid"` // Part of the composite primary key

    CreatedAt time.Time `gorm:"not null;default:CURRENT_TIMESTAMP"`

    // Define relationships back to the parent tables for easier querying
    Workspace Workspace `gorm:"foreignKey:WorkspaceID;references:ID;constraint:OnDelete:CASCADE"`
    Upload    Upload    `gorm:"foreignKey:UploadID;references:ID;constraint:OnDelete:CASCADE"`
}

// TableName specifies the database table name.
func (WorkspaceUpload) TableName() string {
    return "workspace_uploads"
}