package uploadService

// QueueCsvDetails contains the details required to process a CSV file.
type QueueCsvDetails struct {
	// WorkspaceID is the ID of the workspace to which the document belongs
	WorkspaceID string

	// Name of the Document being uploaded
	FileName string

	// Path to the Document being uploaded
	FilePath string

	// Description of the Document being uploaded
	Description string
}