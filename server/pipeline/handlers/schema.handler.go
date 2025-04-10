package handlers

// ProcessHeaderDetails contains the details of the headers in a CSV file.
type CSVDetails struct {
	// The name of the CSV file
	FileName string

	// The size of the CSV file
	FileSize int64

	// The path to the CSV file
	FilePath string

	// The number of rows in the CSV file
	NumRows int

	// The number of columns in the CSV file
	NumCols int

	// The file name of the CSV file
	Headers []string

	// HeadersDescription are the descriptions of the headers
	HeadersDescription map[string]string

	// The headers description
	SampleData map[string]string

	// The Data types of the values under each header
	DataTypes map[string]string
}
