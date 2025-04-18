package models

import (
	"time"

	"database/sql/driver"
	"fmt"
	"strconv"
	"strings"

	"gorm.io/gorm"
)

type EmbeddingSourceType string

const (
	// EmbeddingSourceTypeDocument represents a document source type, which comes from PRISM.
	EmbeddingSourceTypeDocument EmbeddingSourceType = "document"

	// EmbeddingSourceTypeBlock represents a block source type, which comes from PRISM.
	EmbeddingSourceTypeBlock EmbeddingSourceType = "block"

	// EmbeddingSourceTypeCSVColumn represents a CSV, provided by the user.
	EmbeddingSourceTypeCSVColumn EmbeddingSourceType = "csv"

	// EmbeddingSourceTypeOther represents a Postgres SQL Database source type.
	EmbeddingSourceTypePostgresColumn EmbeddingSourceType = "postgres"

	// EmbeddingSourceTypePDFChunk represents a PDF, provided by the user.
	EmbeddingSourceTypePDFChunk EmbeddingSourceType = "pdf_chunk"

	// EmbeddingSourceTypeUserProfile represents a user profile.
	EmbeddingSourceTypeUserProfile EmbeddingSourceType = "user_profile"

	// EmbeddingSourceTypeUserMemory represents the useful user memory, when the user is interacting with PRISM.
	EmbeddingSourceTypeUserMemory EmbeddingSourceType = "user_memory"

	// EmbeddingSourceTypeUnknown represents an unknown source type.
	EmbeddingSourceTypeUnknown EmbeddingSourceType = "unknown"

	// EmbeddingSourceTypePostgresSchema indicates the embedding was generated from the overall Postgres schema description.
	EmbeddingSourceTypePostgresSchema EmbeddingSourceType = "postgres_schema"

	// EmbeddingSourceTypePostgresTable indicates the embedding was generated from a Postgres table description.
	EmbeddingSourceTypePostgresTable EmbeddingSourceType = "postgres_table"

	// EmbeddingSourceTypePostgresView indicates the embedding was generated from a Postgres view description.
	EmbeddingSourceTypePostgresView EmbeddingSourceType = "postgres_view"

	// EmbeddingSourceTypePostgresSummary indicates the embedding was generated from a summary of the entire Postgres schema.
	EmbeddingSourceTypePostgresSummary EmbeddingSourceType = "postgres_summary" // Optional type
)

type VectorEmbedding struct {
	// --- Standard GORM Fields ---
	ID string `gorm:"primaryKey;type:uuid;default:gen_random_uuid()"` // Auto-incrementing primary key for the table (managed by GORM/DB). Uniquely identifies this specific embedding record.

	// CreatedAt time.Time                       // Timestamp automatically set by GORM when the record is first created. Tells you when the embedding was stored.
	CreatedAt time.Time

	// DeletedAt gorm.DeletedAt `gorm:"index"`    // Used for GORM's soft delete feature. Instead of deleting, this timestamp is set. `gorm:"index"` helps query non-deleted records (`WHERE deleted_at IS NULL`) efficiently.
	DeletedAt gorm.DeletedAt `gorm:"index"`

	// SourceType identifies the *kind* of entity the embedding belongs to.
	// Helps categorize the origin of the embedded text.
	// Examples: 'document', 'block', 'csv_column', 'pdf_chunk', 'user_profile'
	SourceType EmbeddingSourceType `gorm:"type:embedding_source_type;not null"` // Custom type for source type. This is a string enum, so it can be stored as a string in the database.

	// SourceIdentifier identifies the specific *instance* of the SourceType.
	// Works together with SourceType to pinpoint the exact origin item.
	// Examples: If SourceType='document', this is the Document's UUID. If SourceType='csv_column', this might be the CSV filename.
	SourceIdentifier string `gorm:"type:text;not null"`

	// RelatedID provides a more granular identifier *within* the SourceIdentifier, if needed.
	// Useful when embedding parts of a larger source.
	// Examples: If embedding specific blocks from a document: SourceIdentifier=DocumentUUID, RelatedID=BlockUUID. If embedding a chunk from a PDF: SourceIdentifier=PDF_Filename, RelatedID=ChunkID/PageNum.
	// It's nullable (`type:text` without `not null`) because sometimes the SourceIdentifier is enough (e.g., embedding a document title).
	RelatedID string `gorm:"type:text"`

	// ColumnOrChunkName gives a specific *name* to the part being embedded, often human-readable.
	// Provides further detail, especially when RelatedID is used.
	// Examples: If embedding a specific column: 'order_total'. If embedding a block: 'heading_1', 'paragraph'. If embedding a section from a document: 'abstract', 'introduction'.
	// Can overlap slightly with RelatedID; establish clear rules for your use case. Nullable.
	ColumnOrChunkName string `gorm:"type:text"`

	// OriginalText stores the actual text snippet that was sent to Gemini to create the embedding vector.
	// Extremely useful for:
	//    1. Debugging: See exactly what text produced a given vector.
	//    2. Context: Show relevant text snippets alongside search results.
	//    3. Verification: Ensure the embedding matches the intended text.
	// Nullable, but highly recommended to store if feasible (can increase storage size).
	OriginalText string `gorm:"type:text"`

	// Embedding holds the actual vector generated by the Gemini embedding model.
	// It uses the custom `PgVector` type you defined (which is essentially `[]float32`).
	// This custom type handles the conversion between the Go slice and the string format `[f1,f2,...]` needed by the PostgreSQL `vector` type via the Scanner/Valuer interfaces.
	// `gorm:"type:vector(768);not null"`:
	//    - `type:vector(768)`: Explicitly tells GORM the database column type is `vector` with 768 dimensions (adjust dimension as needed!).
	//    - `not null`: Ensures that every record must have an embedding vector.
	Embedding PgVector `gorm:"type:vector(768);not null"`
}

// Optional: Define table name explicitly if needed
func (VectorEmbedding) TableName() string {
	return "vector_embeddings"
}

// PgVector is a custom type for handling pgvector data
type PgVector []float32

func (v PgVector) Value() (driver.Value, error) {
	if v == nil {
		return nil, nil
	}
	if len(v) == 0 {
		return "[]", nil
	}

	var sb strings.Builder
	sb.WriteString("[")
	for i, f := range v {
		if i > 0 {
			sb.WriteString(",")
		}
		// 'f', -1, 32 ensures we format as float32 without unnecessary precision
		sb.WriteString(strconv.FormatFloat(float64(f), 'f', -1, 32))
	}
	sb.WriteString("]")
	return sb.String(), nil
}

// Scan implements the sql.Scanner interface for PgVector.
// This converts the string representation "[f1,f2,...]" from the database back into a Go slice []float32.
func (v *PgVector) Scan(value interface{}) error {
	if value == nil {
		*v = nil
		return nil
	}

	var s string
	switch T := value.(type) {
	case []byte:
		s = string(T)
	case string:
		s = T
	default:
		return fmt.Errorf("unsupported scan type for PgVector: %T", value)
	}

	s = strings.TrimSpace(s)
	if !strings.HasPrefix(s, "[") || !strings.HasSuffix(s, "]") {
		if s == "[]" {
			*v = make(PgVector, 0)
			return nil
		}
		return fmt.Errorf("invalid format for PgVector: expected '[...]' but got '%s'", s)
	}
	s = s[1 : len(s)-1]

	if s == "" {
		*v = make(PgVector, 0)
		return nil
	}

	// Split components and parse
	parts := strings.Split(s, ",")
	vec := make(PgVector, len(parts))
	for i, part := range parts {
		f, err := strconv.ParseFloat(strings.TrimSpace(part), 32)
		if err != nil {
			return fmt.Errorf("failed to parse float '%s' in PgVector string: %w", part, err)
		}
		vec[i] = float32(f)
	}
	*v = vec
	return nil
}
