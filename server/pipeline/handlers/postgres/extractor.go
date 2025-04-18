package postgres

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"strings"

	_ "github.com/lib/pq" // PostgreSQL driver
)

// SchemaExtractor handles the extraction of database schema information
type SchemaExtractor struct {
	db     *sql.DB
	schema string // PostgreSQL schema (not our struct schema)
}

// NewSchemaExtractor creates a new schema extractor instance
func NewSchemaExtractor(connectionString string, schema string) (*SchemaExtractor, error) {
	// If no schema specified, use "public"
	if schema == "" {
		schema = "public"
	}

	// Connect to the database
	db, err := sql.Open("postgres", connectionString)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	// Test the connection
	if err := db.Ping(); err != nil {
		db.Close()
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &SchemaExtractor{
		db:     db,
		schema: schema,
	}, nil
}

// Close closes the database connection
func (e *SchemaExtractor) Close() error {
	return e.db.Close()
}

// ExtractSchema extracts the database schema information
func (e *SchemaExtractor) ExtractSchema(ctx context.Context, databaseName string, description string) (*DatabaseSchema, error) {
	// Create the schema structure
	schema := NewDatabaseSchema(databaseName, description)

	// Extract tables
	if err := e.extractTables(ctx, schema); err != nil {
		return nil, err
	}

	// Extract views
	if err := e.extractViews(ctx, schema); err != nil {
		return nil, err
	}

	return schema, nil
}

// extractTables extracts table information from the database
func (e *SchemaExtractor) extractTables(ctx context.Context, schema *DatabaseSchema) error {
	// Query to get all tables in the schema
	query := `
		SELECT table_name, obj_description(pgc.oid, 'pg_class') as table_comment
		FROM pg_catalog.pg_tables t
		JOIN pg_catalog.pg_class pgc ON t.tablename = pgc.relname
		WHERE t.schemaname = $1
		ORDER BY table_name
	`

	rows, err := e.db.QueryContext(ctx, query, e.schema)
	if err != nil {
		return fmt.Errorf("failed to query tables: %w", err)
	}
	defer rows.Close()

	for rows.Next() {
		var tableName, tableComment sql.NullString

		if err := rows.Scan(&tableName, &tableComment); err != nil {
			return fmt.Errorf("failed to scan table row: %w", err)
		}

		table := NewTable(tableName.String, tableComment.String)

		// Extract columns for this table
		if err := e.extractColumns(ctx, table); err != nil {
			return err
		}

		// Extract primary key for this table
		if err := e.extractPrimaryKey(ctx, table); err != nil {
			return err
		}

		// Extract foreign keys for this table
		if err := e.extractForeignKeys(ctx, table); err != nil {
			return err
		}

		// Extract indexes for this table
		// if err := e.extractIndexes(ctx, table); err != nil {
		// 	return err
		// }

		// Get table engine (storage method in PostgreSQL)
		if err := e.extractTableEngine(ctx, table); err != nil {
			return err
		}

		// Add some example values for each column
		if err := e.extractColumnExamples(ctx, table); err != nil {
			return err
		}

		schema.Tables = append(schema.Tables, table)
	}

	return rows.Err()
}

// extractColumns extracts column information for a table
func (e *SchemaExtractor) extractColumns(ctx context.Context, table *Table) error {
	query := `
		SELECT 
			column_name, 
			data_type, 
			character_maximum_length,
			numeric_precision,
			numeric_scale,
			is_nullable = 'YES' as is_nullable,
			column_default,
			pg_get_serial_sequence($2||'.'||$1, column_name) IS NOT NULL as is_serial,
			col_description(
				(SELECT oid FROM pg_catalog.pg_class WHERE relname = $1 AND relnamespace = (
					SELECT oid FROM pg_catalog.pg_namespace WHERE nspname = $2
				)),
				ordinal_position
			) as column_comment
		FROM information_schema.columns
		WHERE table_name = $1 AND table_schema = $2
		ORDER BY ordinal_position
	`

	rows, err := e.db.QueryContext(ctx, query, table.Name, e.schema)
	if err != nil {
		return fmt.Errorf("failed to query columns for table %s: %w", table.Name, err)
	}
	defer rows.Close()

	for rows.Next() {
		var (
			name          string
			dataType      string
			length        sql.NullInt64
			precision     sql.NullInt64
			scale         sql.NullInt64
			nullable      bool
			defaultValue  sql.NullString
			autoIncrement bool
			comment       sql.NullString
		)

		if err := rows.Scan(
			&name, &dataType, &length, &precision, &scale, &nullable,
			&defaultValue, &autoIncrement, &comment,
		); err != nil {
			return fmt.Errorf("failed to scan column row for table %s: %w", table.Name, err)
		}

		column := NewColumn(name, dataType, nullable)

		if length.Valid {
			column.Length = int(length.Int64)
		}

		if precision.Valid {
			column.Precision = int(precision.Int64)
		}

		if scale.Valid {
			column.Scale = int(scale.Int64)
		}

		if defaultValue.Valid {
			column.DefaultValue = defaultValue.String
		}

		column.AutoIncrement = autoIncrement

		if comment.Valid {
			column.Comment = comment.String
		}

		table.Columns = append(table.Columns, column)
	}

	return rows.Err()
}

// extractPrimaryKey extracts primary key information for a table
func (e *SchemaExtractor) extractPrimaryKey(ctx context.Context, table *Table) error {
	query := `
		SELECT kcu.column_name
		FROM information_schema.table_constraints tc
		JOIN information_schema.key_column_usage kcu
			ON tc.constraint_name = kcu.constraint_name
			AND tc.table_schema = kcu.table_schema
			AND tc.table_name = kcu.table_name
		WHERE tc.constraint_type = 'PRIMARY KEY'
			AND tc.table_name = $1
			AND tc.table_schema = $2
		ORDER BY kcu.ordinal_position
	`

	rows, err := e.db.QueryContext(ctx, query, table.Name, e.schema)
	if err != nil {
		return fmt.Errorf("failed to query primary key for table %s: %w", table.Name, err)
	}
	defer rows.Close()

	for rows.Next() {
		var columnName string
		if err := rows.Scan(&columnName); err != nil {
			return fmt.Errorf("failed to scan primary key column for table %s: %w", table.Name, err)
		}
		table.PrimaryKey = append(table.PrimaryKey, columnName)
	}

	return rows.Err()
}

// extractForeignKeys extracts foreign key information for a table
func (e *SchemaExtractor) extractForeignKeys(ctx context.Context, table *Table) error {
	query := `
		SELECT
			tc.constraint_name,
			kcu.column_name,
			ccu.table_name AS referenced_table,
			ccu.column_name AS referenced_column,
			rc.delete_rule,
			rc.update_rule
		FROM information_schema.table_constraints tc
		JOIN information_schema.key_column_usage kcu
			ON tc.constraint_name = kcu.constraint_name
			AND tc.table_schema = kcu.table_schema
		JOIN information_schema.constraint_column_usage ccu
			ON tc.constraint_name = ccu.constraint_name
			AND tc.table_schema = ccu.table_schema
		JOIN information_schema.referential_constraints rc
			ON tc.constraint_name = rc.constraint_name
			AND tc.table_schema = rc.constraint_schema
		WHERE tc.constraint_type = 'FOREIGN KEY'
			AND tc.table_name = $1
			AND tc.table_schema = $2
		ORDER BY tc.constraint_name, kcu.ordinal_position
	`

	rows, err := e.db.QueryContext(ctx, query, table.Name, e.schema)
	if err != nil {
		return fmt.Errorf("failed to query foreign keys for table %s: %w", table.Name, err)
	}
	defer rows.Close()

	// Map to store columns by constraint name
	fkMap := make(map[string]*ForeignKey)

	for rows.Next() {
		var (
			constraintName   string
			columnName       string
			referencedTable  string
			referencedColumn string
			onDelete         string
			onUpdate         string
		)

		if err := rows.Scan(
			&constraintName, &columnName, &referencedTable,
			&referencedColumn, &onDelete, &onUpdate,
		); err != nil {
			return fmt.Errorf("failed to scan foreign key row for table %s: %w", table.Name, err)
		}

		// Get or create the foreign key object
		fk, exists := fkMap[constraintName]
		if !exists {
			fk = NewForeignKey(constraintName, []string{}, referencedTable, []string{})
			fk.OnDelete = onDelete
			fk.OnUpdate = onUpdate
			fkMap[constraintName] = fk
		}

		// Add the column and referenced column
		fk.Columns = append(fk.Columns, columnName)
		fk.RefColumns = append(fk.RefColumns, referencedColumn)
	}

	if err := rows.Err(); err != nil {
		return err
	}

	// Convert map to slice
	for _, fk := range fkMap {
		table.ForeignKeys = append(table.ForeignKeys, fk)
	}

	return nil
}

// extractTableEngine extracts the storage engine for a table
func (e *SchemaExtractor) extractTableEngine(ctx context.Context, table *Table) error {
	// PostgreSQL doesn't have different storage engines like MySQL
	// But we can get the access method which is somewhat equivalent
	query := `
		SELECT am.amname
		FROM pg_catalog.pg_class c
		JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
		JOIN pg_catalog.pg_am am ON am.oid = c.relam
		WHERE c.relname = $1 AND n.nspname = $2
	`

	var engine sql.NullString
	err := e.db.QueryRowContext(ctx, query, table.Name, e.schema).Scan(&engine)
	if err != nil && err != sql.ErrNoRows {
		return fmt.Errorf("failed to get table engine for %s: %w", table.Name, err)
	}

	if engine.Valid {
		table.Engine = engine.String
	} else {
		table.Engine = "heap" // Default PostgreSQL storage
	}

	return nil
}

// extractColumnExamples fetches a few sample values for each column
func (e *SchemaExtractor) extractColumnExamples(ctx context.Context, table *Table) error {
	// For each column, get a few distinct sample values
	for _, column := range table.Columns {
		// Skip large object types
		if strings.Contains(strings.ToLower(column.DataType), "blob") ||
			strings.Contains(strings.ToLower(column.DataType), "bytea") ||
			strings.Contains(strings.ToLower(column.DataType), "binary") {
			continue
		}

		query := fmt.Sprintf(
			"SELECT DISTINCT %s::text FROM %s.%s WHERE %s IS NOT NULL LIMIT 5",
			pqQuoteIdentifier(column.Name),
			pqQuoteIdentifier(e.schema),
			pqQuoteIdentifier(table.Name),
			pqQuoteIdentifier(column.Name),
		)

		rows, err := e.db.QueryContext(ctx, query)
		if err != nil {
			// Just log the error and continue - examples are optional
			log.Printf("Warning: failed to get examples for column %s.%s: %v", table.Name, column.Name, err)
			continue
		}

		for rows.Next() {
			var example sql.NullString
			if err := rows.Scan(&example); err != nil {
				rows.Close()
				return fmt.Errorf("failed to scan example value for column %s.%s: %w", table.Name, column.Name, err)
			}
			if example.Valid {
				column.Examples = append(column.Examples, example.String)
			}
		}

		rows.Close()
		if err := rows.Err(); err != nil {
			return err
		}
	}

	return nil
}

// extractViews extracts view information from the database
func (e *SchemaExtractor) extractViews(ctx context.Context, schema *DatabaseSchema) error {
	// Query to get all views in the schema
	query := `
		SELECT 
			v.table_name AS view_name,
			v.view_definition,
			obj_description(pgc.oid, 'pg_class') as view_comment
		FROM information_schema.views v
		JOIN pg_catalog.pg_class pgc ON v.table_name = pgc.relname
		WHERE v.table_schema = $1
		ORDER BY v.table_name
	`

	rows, err := e.db.QueryContext(ctx, query, e.schema)
	if err != nil {
		return fmt.Errorf("failed to query views: %w", err)
	}
	defer rows.Close()

	for rows.Next() {
		var viewName, definition string
		var comment sql.NullString

		if err := rows.Scan(&viewName, &definition, &comment); err != nil {
			return fmt.Errorf("failed to scan view row: %w", err)
		}

		view := NewView(viewName, definition)

		if comment.Valid {
			view.Comment = comment.String
		}

		// Extract columns for this view
		if err := e.extractViewColumns(ctx, view); err != nil {
			return err
		}

		schema.Views = append(schema.Views, view)
	}

	return rows.Err()
}

// extractViewColumns extracts column information for a view
func (e *SchemaExtractor) extractViewColumns(ctx context.Context, view *View) error {
	query := `
		SELECT 
			column_name, 
			data_type, 
			character_maximum_length,
			numeric_precision,
			numeric_scale,
			is_nullable = 'YES' as is_nullable,
			column_default
		FROM information_schema.columns
		WHERE table_name = $1 AND table_schema = $2
		ORDER BY ordinal_position
	`

	rows, err := e.db.QueryContext(ctx, query, view.Name, e.schema)
	if err != nil {
		return fmt.Errorf("failed to query columns for view %s: %w", view.Name, err)
	}
	defer rows.Close()

	for rows.Next() {
		var (
			name         string
			dataType     string
			length       sql.NullInt64
			precision    sql.NullInt64
			scale        sql.NullInt64
			nullable     bool
			defaultValue sql.NullString
		)

		if err := rows.Scan(
			&name, &dataType, &length, &precision, &scale, &nullable, &defaultValue,
		); err != nil {
			return fmt.Errorf("failed to scan column row for view %s: %w", view.Name, err)
		}

		column := NewColumn(name, dataType, nullable)

		if length.Valid {
			column.Length = int(length.Int64)
		}

		if precision.Valid {
			column.Precision = int(precision.Int64)
		}

		if scale.Valid {
			column.Scale = int(scale.Int64)
		}

		if defaultValue.Valid {
			column.DefaultValue = defaultValue.String
		}

		view.Columns = append(view.Columns, column)
	}

	return rows.Err()
}

// GetRelationships detects relationships between tables
func (e *SchemaExtractor) GetRelationships(ctx context.Context) ([]Relationship, error) {
	var relationships []Relationship

	// First get all foreign keys - these are explicit relationships
	query := `
		SELECT
			tc.table_name AS source_table,
			kcu.column_name AS source_column,
			ccu.table_name AS target_table,
			ccu.column_name AS target_column
		FROM information_schema.table_constraints tc
		JOIN information_schema.key_column_usage kcu
			ON tc.constraint_name = kcu.constraint_name
			AND tc.table_schema = kcu.table_schema
		JOIN information_schema.constraint_column_usage ccu
			ON tc.constraint_name = ccu.constraint_name
			AND tc.table_schema = ccu.table_schema
		WHERE tc.constraint_type = 'FOREIGN KEY'
			AND tc.table_schema = $1
		ORDER BY tc.table_name, tc.constraint_name, kcu.ordinal_position
	`

	rows, err := e.db.QueryContext(ctx, query, e.schema)
	if err != nil {
		return nil, fmt.Errorf("failed to query relationships: %w", err)
	}
	defer rows.Close()

	// Map to group columns by relationship
	relMap := make(map[string]map[string]Relationship)

	for rows.Next() {
		var sourceTable, sourceColumn, targetTable, targetColumn string

		if err := rows.Scan(&sourceTable, &sourceColumn, &targetTable, &targetColumn); err != nil {
			return nil, fmt.Errorf("failed to scan relationship row: %w", err)
		}

		// Create a key for this relationship
		key := fmt.Sprintf("%s->%s", sourceTable, targetTable)

		// Get or create the relationship in our map
		tableMap, exists := relMap[key]
		if !exists {
			tableMap = make(map[string]Relationship)
			relMap[key] = tableMap
		}

		rel, exists := tableMap["fk"]
		if !exists {
			rel = Relationship{
				SourceTable:   sourceTable,
				SourceColumns: []string{},
				TargetTable:   targetTable,
				TargetColumns: []string{},
				IsForeignKey:  true,
			}
		}

		// Add columns to the relationship
		rel.SourceColumns = append(rel.SourceColumns, sourceColumn)
		rel.TargetColumns = append(rel.TargetColumns, targetColumn)
		tableMap["fk"] = rel
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	// Convert map to slice
	for _, tableMap := range relMap {
		for _, rel := range tableMap {
			relationships = append(relationships, rel)
		}
	}

	// TODO: Detect implicit relationships by column name and type matching
	// This can be useful but is more complex - implement if needed

	return relationships, nil
}

// GetTableStatistics collects statistics about table data
func (e *SchemaExtractor) GetTableStatistics(ctx context.Context, tableName string) (*TableStatistics, error) {
	stats := &TableStatistics{
		TableName:   tableName,
		ColumnStats: make(map[string]ColumnStats),
	}

	// Get row count
	countQuery := fmt.Sprintf(
		"SELECT COUNT(*) FROM %s.%s",
		pqQuoteIdentifier(e.schema),
		pqQuoteIdentifier(tableName),
	)

	err := e.db.QueryRowContext(ctx, countQuery).Scan(&stats.RowCount)
	if err != nil {
		return nil, fmt.Errorf("failed to get row count for table %s: %w", tableName, err)
	}

	// Get table size
	sizeQuery := `
		SELECT pg_total_relation_size($1::regclass::oid)
	`
	fullTableName := fmt.Sprintf("%s.%s", e.schema, tableName)
	err = e.db.QueryRowContext(ctx, sizeQuery, fullTableName).Scan(&stats.SizeBytes)
	if err != nil {
		// Just log and continue - size is optional
		log.Printf("Warning: failed to get table size for %s: %v", tableName, err)
	}

	// Get columns for this table
	colQuery := `
		SELECT column_name, data_type
		FROM information_schema.columns
		WHERE table_name = $1 AND table_schema = $2
		ORDER BY ordinal_position
	`

	colRows, err := e.db.QueryContext(ctx, colQuery, tableName, e.schema)
	if err != nil {
		return nil, fmt.Errorf("failed to get columns for table %s: %w", tableName, err)
	}
	defer colRows.Close()

	// Process each column
	for colRows.Next() {
		var colName, dataType string
		if err := colRows.Scan(&colName, &dataType); err != nil {
			return nil, fmt.Errorf("failed to scan column info for table %s: %w", tableName, err)
		}

		colStats, err := e.getColumnStatistics(ctx, tableName, colName, dataType)
		if err != nil {
			// Just log and continue - column stats are optional
			log.Printf("Warning: failed to get stats for column %s.%s: %v", tableName, colName, err)
			continue
		}

		stats.ColumnStats[colName] = colStats
	}

	if err := colRows.Err(); err != nil {
		return nil, err
	}

	return stats, nil
}

// getColumnStatistics collects statistics about a specific column
func (e *SchemaExtractor) getColumnStatistics(ctx context.Context, tableName, colName, dataType string) (ColumnStats, error) {
	var stats ColumnStats

	// Quote identifiers for use in dynamic SQL
	quotedSchema := pqQuoteIdentifier(e.schema)
	quotedTable := pqQuoteIdentifier(tableName)
	quotedCol := pqQuoteIdentifier(colName)

	// Get null count
	nullQuery := fmt.Sprintf(
		"SELECT COUNT(*) FROM %s.%s WHERE %s IS NULL",
		quotedSchema, quotedTable, quotedCol,
	)

	err := e.db.QueryRowContext(ctx, nullQuery).Scan(&stats.NullCount)
	if err != nil {
		return stats, fmt.Errorf("failed to get null count for column %s.%s: %w", tableName, colName, err)
	}

	// Get distinct count
	distinctQuery := fmt.Sprintf(
		"SELECT COUNT(DISTINCT %s) FROM %s.%s",
		quotedCol, quotedSchema, quotedTable,
	)

	err = e.db.QueryRowContext(ctx, distinctQuery).Scan(&stats.DistinctCount)
	if err != nil {
		return stats, fmt.Errorf("failed to get distinct count for column %s.%s: %w", tableName, colName, err)
	}

	// For numeric columns, get min and max
	isNumeric := strings.Contains(strings.ToLower(dataType), "int") ||
		strings.Contains(strings.ToLower(dataType), "float") ||
		strings.Contains(strings.ToLower(dataType), "numeric") ||
		strings.Contains(strings.ToLower(dataType), "decimal")

	if isNumeric {
		minMaxQuery := fmt.Sprintf(
			"SELECT MIN(%s), MAX(%s) FROM %s.%s",
			quotedCol, quotedCol, quotedSchema, quotedTable,
		)

		var minVal, maxVal sql.NullString
		err := e.db.QueryRowContext(ctx, minMaxQuery).Scan(&minVal, &maxVal)
		if err != nil {
			return stats, fmt.Errorf("failed to get min/max for column %s.%s: %w", tableName, colName, err)
		}

		if minVal.Valid {
			stats.MinValue = minVal.String
		}

		if maxVal.Valid {
			stats.MaxValue = maxVal.String
		}
	}

	// For string columns, get average length
	isString := strings.Contains(strings.ToLower(dataType), "char") ||
		strings.Contains(strings.ToLower(dataType), "text")

	if isString {
		avgLengthQuery := fmt.Sprintf(
			"SELECT AVG(LENGTH(%s)) FROM %s.%s WHERE %s IS NOT NULL",
			quotedCol, quotedSchema, quotedTable, quotedCol,
		)

		err := e.db.QueryRowContext(ctx, avgLengthQuery).Scan(&stats.AvgLength)
		if err != nil {
			return stats, fmt.Errorf("failed to get avg length for column %s.%s: %w", tableName, colName, err)
		}
	}

	// Get value distribution for low-cardinality columns
	// Only if distinct count is reasonably small (e.g., less than 20)
	if stats.DistinctCount > 0 && stats.DistinctCount < 20 {
		stats.ValueDistribution = make(map[string]int64)

		distQuery := fmt.Sprintf(
			"SELECT %s::text, COUNT(*) FROM %s.%s WHERE %s IS NOT NULL GROUP BY %s ORDER BY COUNT(*) DESC",
			quotedCol, quotedSchema, quotedTable, quotedCol, quotedCol,
		)

		distRows, err := e.db.QueryContext(ctx, distQuery)
		if err != nil {
			return stats, fmt.Errorf("failed to get value distribution for column %s.%s: %w", tableName, colName, err)
		}
		defer distRows.Close()

		for distRows.Next() {
			var value string
			var count int64
			if err := distRows.Scan(&value, &count); err != nil {
				return stats, fmt.Errorf("failed to scan value distribution for column %s.%s: %w", tableName, colName, err)
			}
			stats.ValueDistribution[value] = count
		}

		if err := distRows.Err(); err != nil {
			return stats, err
		}
	}

	return stats, nil
}

// Helper function to properly quote PostgreSQL identifiers
func pqQuoteIdentifier(name string) string {
	return `"` + strings.Replace(name, `"`, `""`, -1) + `"`
}

// extractIndexes extracts index information for a table
// func (e *SchemaExtractor) extractIndexes(ctx context.Context, table *Table) error {
// 	query := `
// 		SELECT
// 			i.relname AS index_name,
// 			ix.indisunique AS is_unique,
// 			CASE
// 				WHEN am.amname = 'btree' THEN 'BTREE'
// 				WHEN am.amname = 'hash' THEN 'HASH'
// 				WHEN am.amname = 'gin' THEN 'GIN'
// 				WHEN am.amname = 'gist' THEN 'GIST'
// 				ELSE am.amname
// 			END AS index_type,
// 			array_agg(a.attname ORDER BY array_position(ix.indkey, a.attnum)) AS column_names,
// 			array_agg(
// 				CASE
// 					WHEN am.amname = 'btree' THEN
// 						CASE
// 							WHEN array_position(ix.indoption, 0) = array_position(ix.indkey, a.attnum) THEN 'ASC'
// 							ELSE 'DESC'
// 						END
// 					ELSE NULL
// 				END
// 				ORDER BY array_position(ix.indkey, a.attnum)
// 			) AS column_orders
// 		FROM pg_catalog.pg_index ix
// 		JOIN pg_catalog.pg_class i ON i.oid = ix.indexrelid
// 		JOIN pg_catalog.pg_class t ON t.oid = ix.indrelid
// 		JOIN pg_catalog.pg_namespace n ON n.oid = t.relnamespace
// 		JOIN pg_catalog.pg_am am ON am.oid = i.relam
// 		JOIN pg_catalog.pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
// 		WHERE t.relname = $1
// 			AND n.nspname = $2
// 			AND NOT ix.indisprimary  -- Exclude primary keys as they're handled separately
// 		GROUP BY i.relname, ix.indisunique, am.amname
// 	`

// 	rows, err := e.db.QueryContext(ctx, query, table.Name, e.schema)
// 	if err != nil {
// 		return fmt.Errorf("failed to query indexes for table %s: %w", table.Name, err)
// 	}
// 	defer rows.Close()

// 	for rows.Next() {
// 		var (
// 			indexName    string
// 			isUnique     bool
// 			indexType    string
// 			columnNames  []string
// 			columnOrders []sql.NullString
// 		)

// 		if err := rows.Scan(&indexName, &isUnique, &indexType, &columnNames, &columnOrders); err != nil {
// 			return fmt.Errorf("failed to scan index row for table %s: %w", table.Name, err)
// 		}

// 		index := NewIndex(indexName, isUnique)
// 		index.Type = indexType

// 		// Add columns to the index
// 		for i, colName := range columnNames {
// 			var order string
// 			if columnOrders[i].Valid {
// 				order = columnOrders[i].String
// 			}
// 			index.Columns = append(index.Columns, IndexColumn{
// 				Name:  colName,
// 				Order: order,
// 			})
// 		}

// 		table.Indexes = append(table.Indexes, index)
// 	}

// 	return rows.Err()
// }
