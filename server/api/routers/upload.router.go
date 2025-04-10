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

	filePath := "/Users/omg/Desktop/01/shooting-star/server/data/mock_file_2.csv"

	csvHandler := handlers.NewCSVHandler(d.ctx)
	defer csvHandler.Close()

	csvDetails, err := csvHandler.ExtractCSVDetails(filePath)
	if err != nil {
		d.logger.Error("Error extracting CSV details", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, "Failed to extract CSV details")
	}

	err = csvHandler.ProcessAndEmbedCSV(csvDetails)
	if err != nil {
		d.logger.Error("Error processing CSV file", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, "Failed to process CSV file")
	}

	return responses.OK(c, "CSV file processed successfully")
}