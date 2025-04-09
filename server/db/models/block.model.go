package models

import (
	"encoding/json"
	"errors"
	"time"

	"gorm.io/gorm"
)

type BlockType string

const (
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
)

type Block struct {
	ID string `gorm:"primaryKey;type:uuid;default:gen_random_uuid()" json:"id"`
	
	// Document ID to which this block belongs
	DocumentID string `gorm:"type:uuid;not null;index;constraint:OnDelete:CASCADE"`
	
	// Block type and content
	Type    BlockType       `gorm:"type:varchar(255);not null" json:"blockType"`
	Content BlockContentJSON `gorm:"type:jsonb;not null" json:"content"`
	
	// Standard timestamps
	CreatedAt time.Time      `json:"createdAt"`
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

func (Block) TableName() string {
    return "blocks"
}