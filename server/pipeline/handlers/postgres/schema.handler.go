package postgres

import "time"

type DatabaseSchema struct {
	Name        string    `json:"name"`
	Description string    `json:"description,omitempty"`
	Tables      []*Table  `json:"tables"`
	Views       []*View   `json:"views,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
}

// NewDatabaseSchema creates a new DatabaseSchema instance
func NewDatabaseSchema(name string, description string) *DatabaseSchema {
	return &DatabaseSchema{
		Name:        name,
		Description: description,
		Tables:      []*Table{},
		Views:       []*View{},
		CreatedAt:   time.Now(),
	}
}

// Table represents a database table
type Table struct {
	Name        string        `json:"name"`
	Description string        `json:"description,omitempty"`
	Columns     []*Column     `json:"columns"`
	PrimaryKey  []string      `json:"primary_key,omitempty"`
	ForeignKeys []*ForeignKey `json:"foreign_keys,omitempty"`
	Indexes     []*Index      `json:"indexes,omitempty"`
	Engine      string        `json:"engine,omitempty"`
	Comment     string        `json:"comment,omitempty"`
}

// NewTable creates a new Table instance
func NewTable(name string, description string) *Table {
	return &Table{
		Name:        name,
		Description: description,
		Columns:     []*Column{},
		PrimaryKey:  []string{},
		ForeignKeys: []*ForeignKey{},
		Indexes:     []*Index{},
	}
}

// Column represents a table column
type Column struct {
	Name          string      `json:"name"`
	DataType      string      `json:"data_type"`
	Length        int         `json:"length,omitempty"`
	Precision     int         `json:"precision,omitempty"`
	Scale         int         `json:"scale,omitempty"`
	Nullable      bool        `json:"nullable"`
	DefaultValue  interface{} `json:"default_value,omitempty"`
	AutoIncrement bool        `json:"auto_increment,omitempty"`
	Comment       string      `json:"comment,omitempty"`
	Examples      []string    `json:"examples,omitempty"` // Example values from the data
}

// NewColumn creates a new Column instance
func NewColumn(name string, dataType string, nullable bool) *Column {
	return &Column{
		Name:     name,
		DataType: dataType,
		Nullable: nullable,
		Examples: []string{},
	}
}

// ForeignKey represents a foreign key relationship
type ForeignKey struct {
	Name       string   `json:"name"`
	Columns    []string `json:"columns"`
	RefTable   string   `json:"referenced_table"`
	RefColumns []string `json:"referenced_columns"`
	OnDelete   string   `json:"on_delete,omitempty"`
	OnUpdate   string   `json:"on_update,omitempty"`
}

// NewForeignKey creates a new ForeignKey instance
func NewForeignKey(name string, columns []string, refTable string, refColumns []string) *ForeignKey {
	return &ForeignKey{
		Name:       name,
		Columns:    columns,
		RefTable:   refTable,
		RefColumns: refColumns,
	}
}

// Index represents a database index
type Index struct {
	Name    string        `json:"name"`
	Columns []IndexColumn `json:"columns"`
	Unique  bool          `json:"unique,omitempty"`
	Type    string        `json:"type,omitempty"` // BTREE, HASH, etc.
}

// IndexColumn represents a column in an index with its order
type IndexColumn struct {
	Name  string `json:"name"`
	Order string `json:"order,omitempty"` // ASC or DESC
}

// NewIndex creates a new Index instance
func NewIndex(name string, unique bool) *Index {
	return &Index{
		Name:    name,
		Columns: []IndexColumn{},
		Unique:  unique,
	}
}

// View represents a database view
type View struct {
	Name       string    `json:"name"`
	Definition string    `json:"definition"`
	Columns    []*Column `json:"columns,omitempty"`
	Comment    string    `json:"comment,omitempty"`
}

// NewView creates a new View instance
func NewView(name string, definition string) *View {
	return &View{
		Name:       name,
		Definition: definition,
		Columns:    []*Column{},
	}
}

// TableStatistics represents statistics about a table's data
type TableStatistics struct {
	TableName   string                 `json:"table_name"`
	RowCount    int64                  `json:"row_count"`
	SizeBytes   int64                  `json:"size_bytes,omitempty"`
	ColumnStats map[string]ColumnStats `json:"column_stats,omitempty"`
}

// ColumnStats represents statistics about a column's data
type ColumnStats struct {
	NullCount         int64            `json:"null_count"`
	DistinctCount     int64            `json:"distinct_count"`
	MinValue          interface{}      `json:"min_value,omitempty"`
	MaxValue          interface{}      `json:"max_value,omitempty"`
	AvgLength         float64          `json:"avg_length,omitempty"`         // For string/blob types
	ValueDistribution map[string]int64 `json:"value_distribution,omitempty"` // For low-cardinality columns
}

// Relationship represents a detected relationship between tables
type Relationship struct {
	SourceTable   string   `json:"source_table"`
	SourceColumns []string `json:"source_columns"`
	TargetTable   string   `json:"target_table"`
	TargetColumns []string `json:"target_columns"`
	IsForeignKey  bool     `json:"is_foreign_key"` // Whether this relationship is defined as a FK
}
