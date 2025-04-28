package routers

import (
	"context"

	"github.com/OmGuptaIND/shooting-star/api/responses"
	"github.com/OmGuptaIND/shooting-star/api/schema"
	"github.com/OmGuptaIND/shooting-star/appError"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	uploadService "github.com/OmGuptaIND/shooting-star/services/upload"
	"github.com/gofiber/fiber/v3"
	"go.uber.org/zap"
)

// DocumentRouter handles the routing for document-related endpoints.
type UploadRouter struct {
	ctx context.Context
	logger *zap.Logger
}

// NewDocumentRouter creates a new DocumentRouter instance with the provided fiber.Router.
func RegisterUploadRouter(ctx context.Context, baseRouter fiber.Router) {
	handler := &UploadRouter{
		ctx: ctx,
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

	err := uploadService.Service.QueueCsvUpload(&uploadService.QueueCsvDetails{
		WorkspaceID: req.WorkspaceID,
		FileName:   req.FileName,
		FilePath:  req.FilePath,
		Description: req.Description,
	})
	if err != nil {
		d.logger.Error("Error uploading CSV file", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, err.Error())
	}


	response := &schema.UploadCsvResponse{
		Message: "CSV file Queued for processing",
	}

	return responses.Accepted(c, response)
}