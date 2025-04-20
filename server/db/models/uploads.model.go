package models

import (
	"time"

	"gorm.io/gorm"
)

// UploadType defines the allowed types for upload sources.
type UploadType string

const (
	// UploadTypeDocument represents a document source type (e.g., from PRISM).
	UploadTypeDocument UploadType = "document"

	// UploadTypeBlock represents a block source type (e.g., from PRISM).
	UploadTypeBlock UploadType = "block"

	// UploadTypeCSV represents a CSV file provided by the user.
	UploadTypeCSV UploadType = "csv"

	// UploadTypePDF represents a PDF file provided by the user.
	UploadTypePDF UploadType = "pdf" // Corrected comment
)

// Uploads table stores information about the files uploaded by users.
type Upload struct {
	// ID is the unique identifier for each upload record (UUID v4).
	ID string `gorm:"primaryKey;type:uuid;default:gen_random_uuid()"` // Unique UUID primary key.

	// CreatedAt timestamp is automatically set by GORM when the record is first created.
	CreatedAt time.Time // Automatically managed by GORM.

	// DeletedAt timestamp is used for GORM's soft delete feature.
	// Records are marked as deleted instead of being permanently removed.
	// `gorm:"index"` helps query non-deleted records efficiently.
	DeletedAt gorm.DeletedAt `gorm:"index"` // Standard GORM soft delete field.

	// SourceType identifies the *kind* of entity the upload represents.
	// Helps categorize the origin of the uploaded file.
	// e.g., Document, Block, CSV, PDF, SQL, etc.
	SourceType UploadType `gorm:"index;type:upload_type;not null"` // Custom enum type, indexed for faster filtering by type.

	// SourceIdentifier identifies the specific *instance* of the SourceType.
	// Works with SourceType to pinpoint the exact origin item (e.g., WorkspaceUUID, Document UUID, Block ID).
	// Added index for faster lookups based on the source identifier.
	SourceIdentifier string `gorm:"index;type:text;not null"` // Identifier for the source, indexed.

	// FileLocation provides the storage path or URL of the uploaded file.
	FileLocation string `gorm:"type:text;not null"` // Location of the file (e.g., S3 path, local path).

	// WorkspaceID is the ID of the workspace associated with the upload.
	WorkspaceUploads []WorkspaceUpload `gorm:"foreignKey:UploadID" json:"-"`
}

// TableName specifies the database table name for the Uploads model.
func (Upload) TableName() string {
	return "uploads"
}