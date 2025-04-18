package postgres

import (
	"context"
	"fmt"
	"strconv"
	"strings"

	// Import time if needed for context timeouts/deadlines
	"github.com/OmGuptaIND/shooting-star/appError"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/db"                // Assuming your GORM connection is here
	"github.com/OmGuptaIND/shooting-star/db/models"         // Assuming models are here
	"github.com/OmGuptaIND/shooting-star/pipeline/provider" // Assuming AI provider is here
	"github.com/google/generative-ai-go/genai"
	"go.uber.org/zap"
	// Import gorm for potential DB interactions
)

// postgresHandler handles operations related to PostgreSQL database schemas.
type postgresHandler struct {
	ctx        context.Context
	cancelFunc context.CancelFunc

	logger *zap.Logger
}

// NewPostgresHandler creates a new instance of postgresHandler with the provided context.
func NewPostgresHandler(ctx context.Context) *postgresHandler {
	ctx, cancelFunc := context.WithCancel(ctx) // Create cancellable context

	return &postgresHandler{
		ctx:        ctx,
		cancelFunc: cancelFunc,
		logger:     logger.FromCtx(ctx).With(zap.String("handler", "postgresHandler")),
	}
}

// Close cancels the context of the postgresHandler, allowing for cleanup.
func (h *postgresHandler) Close() {
	h.cancelFunc()
}

// ProcessAndEmbedPostgresSchema generates embeddings for a PostgreSQL schema,
// its tables, columns, and views, and stores them in the database.
// schemaSourceID should be a unique identifier for this schema snapshot,
// likely the ID of a record representing this schema discovery/upload.
func (h *postgresHandler) ProcessAndEmbedPostgresSchema(schema *DatabaseSchema, schemaSourceID uint) error {
	h.logger.Info("Processing and embedding PostgreSQL schema", zap.String("schemaName", schema.Name), zap.Uint("schemaSourceID", schemaSourceID))

	genClient, err := provider.NewGeminiProvider(h.ctx)
	if err != nil {
		return appError.New(appError.InternalError, "failed to create Gemini client", err)
	}
	defer genClient.Close()

	// Use the same embedding model as the CSV handler for consistency
	em := genClient.EmbeddingModel(string(provider.Embedding001))

	// Create a new batch for embedding
	b := em.NewBatch()

	// Slice to hold candidates before embedding, used to map results back
	type embeddingCandidate struct {
		SourceType        models.EmbeddingSourceType
		SourceIdentifier  string // Database/Schema Name
		ColumnOrChunkName string // Name of the embedded item (schema name, table name, column name, view name)
		OriginalText      string // The text sent to the embedding model
	}
	var candidates []*embeddingCandidate

	// 1. Add Schema Description to batch
	schemaTitle := fmt.Sprintf("Database Schema: %s", schema.Name)
	// You could add more context here, e.g., num tables/views, creation date
	schemaContent := fmt.Sprintf("Database Schema Name: %s\nDescription: %s", schema.Name, schema.Description)

	b.AddContentWithTitle(schemaTitle, genai.Text(schemaContent))
	candidates = append(candidates, &embeddingCandidate{
		SourceType:        models.EmbeddingSourceTypePostgresColumn,
		SourceIdentifier:  schema.Name,
		ColumnOrChunkName: schema.Name, // Use schema name as item name
		OriginalText:      schemaContent,
	})
	h.logger.Debug("Added schema to embedding batch", zap.String("name", schema.Name))

	// 2. Add Tables to batch
	for _, table := range schema.Tables {
		tableTitle := fmt.Sprintf("Database Schema: %s, Table: %s", schema.Name, table.Name)

		// Build descriptive content for the table
		tableContent := fmt.Sprintf(
			"Database Table Name: %s\nDescription: %s\nPrimary Key: %s\nColumns: %s\nForeign Keys: %s\nIndexes: %s\nComment: %s",
			table.Name,
			table.Description,
			formatStrings(table.PrimaryKey),      // Helper to format string slice
			formatColumns(table.Columns),         // Helper to format column list
			formatForeignKeys(table.ForeignKeys), // Helper to format FK list
			formatIndexes(table.Indexes),         // Helper to format Index list
			table.Comment,
		)

		b.AddContentWithTitle(tableTitle, genai.Text(tableContent))
		candidates = append(candidates, &embeddingCandidate{
			SourceType:        models.EmbeddingSourceTypePostgresTable,
			SourceIdentifier:  schema.Name,
			ColumnOrChunkName: table.Name, // Use table name as item name
			OriginalText:      tableContent,
		})
		h.logger.Debug("Added table to embedding batch", zap.String("tableName", table.Name))

		// 3. Add Columns to batch (nested within tables)
		for _, column := range table.Columns {
			columnTitle := fmt.Sprintf("Database Schema: %s, Table: %s, Column: %s", schema.Name, table.Name, column.Name)

			// Build descriptive content for the column
			columnContent := fmt.Sprintf(
				"Database Column Name: %s\nDataType: %s\nNullable: %t\nDefault Value: %s\nComment: %s\nExamples: %s",
				column.Name,
				column.DataType,
				column.Nullable,
				formatDefaultValue(column.DefaultValue), // Helper for default value
				column.Comment,
				formatExamples(column.Examples), // Helper for examples
			)

			b.AddContentWithTitle(columnTitle, genai.Text(columnContent))
			candidates = append(candidates, &embeddingCandidate{
				SourceType:        models.EmbeddingSourceTypePostgresColumn,
				SourceIdentifier:  schema.Name + "." + table.Name, // Use "schema.table" for context
				ColumnOrChunkName: column.Name,                    // Use column name as item name
				OriginalText:      columnContent,
			})
			h.logger.Debug("Added column to embedding batch", zap.String("columnName", column.Name), zap.String("tableName", table.Name))
		}
	}

	// 4. Add Views to batch
	for _, view := range schema.Views {
		viewTitle := fmt.Sprintf("Database Schema: %s, View: %s", schema.Name, view.Name)

		// Build descriptive content for the view
		viewContent := fmt.Sprintf(
			"Database View Name: %s\nDefinition: %s\nComment: %s\nColumns: %s",
			view.Name,
			view.Definition,
			view.Comment,
			formatColumns(view.Columns), // Helper to format column list (if views have columns populated)
		)

		b.AddContentWithTitle(viewTitle, genai.Text(viewContent))
		candidates = append(candidates, &embeddingCandidate{
			SourceType:        models.EmbeddingSourceTypePostgresView,
			SourceIdentifier:  schema.Name,
			ColumnOrChunkName: view.Name, // Use view name as item name
			OriginalText:      viewContent,
		})
		h.logger.Debug("Added view to embedding batch", zap.String("viewName", view.Name))
	}

	if len(candidates) == 0 {
		h.logger.Info("No schema elements found to embed", zap.String("schemaName", schema.Name))
		return nil // Nothing to embed
	}

	h.logger.Info("Sending embedding batch to Gemini", zap.Int("count", len(candidates)))
	res, err := em.BatchEmbedContents(h.ctx, b)
	if err != nil {
		h.logger.Error("Failed to get embeddings from Gemini", zap.Error(err))
		return appError.New(appError.InternalError, err.Error(), err)
	}

	if len(res.Embeddings) != len(candidates) {
		h.logger.Error("Mismatch between number of embedding candidates and results",
			zap.Int("candidates", len(candidates)),
			zap.Int("results", len(res.Embeddings)),
			zap.String("schemaName", schema.Name),
		)
		return appError.New(appError.InternalError, "mismatch in embedding results count", nil)
	}

	// Prepare embeddings for database storage
	vectorEmbeddings := make([]*models.VectorEmbedding, 0, len(res.Embeddings))

	for i, e := range res.Embeddings {
		candidate := candidates[i] // Get the original candidate corresponding to this result

		vectorEmbedding := &models.VectorEmbedding{
			SourceType:        candidate.SourceType,
			RelatedID:         strconv.FormatUint(uint64(schemaSourceID), 10), // Use the ID provided for this schema source
			SourceIdentifier:  candidate.SourceIdentifier,
			ColumnOrChunkName: candidate.ColumnOrChunkName,
			OriginalText:      candidate.OriginalText,
			Embedding:         e.Values,
		}

		vectorEmbeddings = append(vectorEmbeddings, vectorEmbedding)
	}

	h.logger.Info("Storing generated embeddings in database", zap.Int("count", len(vectorEmbeddings)), zap.Uint("schemaSourceID", schemaSourceID))
	// Store embeddings in batches
	if err := db.Conn.CreateInBatches(vectorEmbeddings, 100).Error; err != nil { // Adjust batch size as needed
		h.logger.Error("Failed to store vector embeddings", zap.Error(err))
		return appError.New(appError.InternalError, "failed to store vector embeddings", err)
	}

	h.logger.Info("PostgreSQL schema processed and embeddings stored successfully", zap.String("schemaName", schema.Name), zap.Uint("schemaSourceID", schemaSourceID))

	return nil
}

// --- Helper functions to format struct data into strings for embedding ---

func formatStrings(s []string) string {
	if len(s) == 0 {
		return "None"
	}
	// Limit the number of items listed to keep the content concise
	if len(s) > 5 {
		return strings.Join(s[:5], ", ") + ", ..."
	}
	return strings.Join(s, ", ")
}

func formatColumns(cols []*Column) string {
	if len(cols) == 0 {
		return "None"
	}
	columnNames := make([]string, len(cols))
	for i, col := range cols {
		columnNames[i] = col.Name
	}
	// Limit the number of items listed
	if len(columnNames) > 10 {
		return strings.Join(columnNames[:10], ", ") + ", ..."
	}
	return strings.Join(columnNames, ", ")
}

func formatForeignKeys(fks []*ForeignKey) string {
	if len(fks) == 0 {
		return "None"
	}
	fkStrings := make([]string, 0, len(fks))
	for _, fk := range fks {
		// Format: (cols) -> RefTable(RefCols)
		fkString := fmt.Sprintf("(%s) -> %s(%s)",
			formatStrings(fk.Columns),
			fk.RefTable,
			formatStrings(fk.RefColumns),
		)
		fkStrings = append(fkStrings, fkString)
	}
	// Limit the number of items listed
	if len(fkStrings) > 3 {
		return strings.Join(fkStrings[:3], "; ") + "; ..."
	}
	return strings.Join(fkStrings, "; ")
}

func formatIndexes(indexes []*Index) string {
	if len(indexes) == 0 {
		return "None"
	}
	indexStrings := make([]string, 0, len(indexes))
	for _, idx := range indexes {
		// Format: Name (Cols) [Type] [Unique]
		idxString := fmt.Sprintf("%s (%s)",
			idx.Name,
			formatIndexColumns(idx.Columns),
		)
		parts := []string{}
		if idx.Type != "" {
			parts = append(parts, idx.Type)
		}
		if idx.Unique {
			parts = append(parts, "UNIQUE")
		}
		if len(parts) > 0 {
			idxString += fmt.Sprintf(" [%s]", strings.Join(parts, " "))
		}
		indexStrings = append(indexStrings, idxString)
	}
	// Limit the number of items listed
	if len(indexStrings) > 3 {
		return strings.Join(indexStrings[:3], "; ") + "; ..."
	}
	return strings.Join(indexStrings, "; ")
}

func formatIndexColumns(cols []IndexColumn) string {
	if len(cols) == 0 {
		return ""
	}
	colStrings := make([]string, len(cols))
	for i, col := range cols {
		colStrings[i] = col.Name
		if col.Order != "" {
			colStrings[i] += " " + col.Order
		}
	}
	return strings.Join(colStrings, ", ")
}

func formatDefaultValue(v interface{}) string {
	if v == nil {
		return "None"
	}
	// Handle different types if necessary, otherwise use default string conversion
	return fmt.Sprintf("%v", v)
}

func formatExamples(examples []string) string {
	if len(examples) == 0 {
		return "None"
	}
	// Limit and join examples
	if len(examples) > 3 {
		return strings.Join(examples[:3], ", ") + ", ..."
	}
	return strings.Join(examples, ", ")
}
