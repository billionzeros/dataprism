package routers

import (
	"context"

	"github.com/OmGuptaIND/shooting-star/api/responses"
	"github.com/OmGuptaIND/shooting-star/api/schema"
	"github.com/OmGuptaIND/shooting-star/appError"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/pipeline/handlers"
	"github.com/OmGuptaIND/shooting-star/services"
	"github.com/gofiber/fiber/v3"
	"go.uber.org/zap"
)

// DocumentRouter handles the routing for document-related endpoints.
type UploadRouter struct {
	ctx context.Context
	uploadService services.UploadService
	logger *zap.Logger
}

// NewDocumentRouter creates a new DocumentRouter instance with the provided fiber.Router.
func RegisterUploadRouter(ctx context.Context, baseRouter fiber.Router) {
	handler := &UploadRouter{
		ctx: ctx,
		uploadService: services.NewUploadService(ctx),
		logger: logger.FromCtx(ctx),
	}

	// Grouping the routes under `/documents`
	uploadGroup := baseRouter.Group("/upload")

	uploadGroup.Post("/csv", handler.uploadCsv) // Upload a CSV file
}

// uploadCsv handles the upload of a CSV file and processes it.
func (d *UploadRouter) uploadCsv(c fiber.Ctx) error {
	req := new(schema.UploadCsvRequest)

	if err := c.Bind().Body(&req); err != nil {
		d.logger.Error("Error binding request body", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, "Invalid request body")
	}

	if req.FileName == "" || req.FilePath == "" {
		d.logger.Error("Invalid request parameters", zap.String("fileName", req.FileName), zap.String("filePath", req.FilePath))
		return responses.BadRequest(c, appError.InternalError, "File name and file path are required")
	}

	d.logger.Info("Received CSV upload request", zap.String("fileName", req.FileName))

	csvHandler := handlers.NewCSVHandler(d.ctx)
	defer csvHandler.Close()

	csvDetails, err := csvHandler.ExtractCSVDetails(req.FilePath)
	if err != nil {
		d.logger.Error("Error extracting CSV details", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, "Failed to extract CSV details")
	}

	uploadInfo, err := csvHandler.UploadCSV(csvDetails)
	if err != nil {
		d.logger.Error("Error uploading CSV file", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, "Failed to upload CSV file")
	}

	// Set the upload information in the CSV details
	csvDetails.UploadInfo = uploadInfo

	err = csvHandler.ProcessAndEmbedCSV(csvDetails)
	if err != nil {
		d.logger.Error("Error processing CSV file", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, "Failed to process CSV file")
	}

	return responses.OK(c, "CSV file Processed Successfully")
}