package routers

import (
	"context"
	"errors"

	"github.com/OmGuptaIND/shooting-star/api/responses"
	"github.com/OmGuptaIND/shooting-star/appError"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/db/models"
	"github.com/OmGuptaIND/shooting-star/services/documents"
	"github.com/gofiber/fiber/v3"
	"go.uber.org/zap"
	"gorm.io/gorm"
)

// DocumentRouter handles the routing for document-related endpoints.
type DocumentRouter struct {
	ctx context.Context
	documentService documents.DocumentService

	logger *zap.Logger
}

// NewDocumentRouter creates a new DocumentRouter instance with the provided fiber.Router.
func RegisterDocumentRoutes(ctx context.Context, baseRouter fiber.Router) {
	handler := &DocumentRouter{
		ctx: context.WithoutCancel(ctx),
		logger: logger.FromCtx(ctx),
	}

	documentGroup := baseRouter.Group("/documents")

	documentGroup.Post("/create", handler.createDocument)
	documentGroup.Get("/:id", handler.getDocumentById)
}

// createDocument handles the creation of a new document.
func (d *DocumentRouter) createDocument(c fiber.Ctx) error {
	req := new(documents.CreateDocumentRequest)

	if err := c.Bind().Body(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Invalid request body",
		})
	}

	doc, err := d.documentService.CreateDocument(&models.Document{
		Title: req.Title,
	})
	if err != nil {
		d.logger.Error("Error creating document", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, err.Error())
	}

	d.logger.Info("document created", zap.String("title", req.Title))

	return responses.Created(c, doc)
}

// getDocumentById handles the retrieval of a document by its ID.
func (d *DocumentRouter) getDocumentById(c fiber.Ctx) error {
	req := new(documents.GetDocumentByIDRequest)

	if err := c.Bind().Body(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Invalid request body",
		})
	}

	doc, err := d.documentService.GetDocumentByID(req.ID)
	if err != nil {
		d.logger.Error("Error retrieving document", zap.Error(err))
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return responses.NotFound(c, appError.NotFound, "Document not found")
		}

		return responses.BadRequest(c, appError.InternalError, err.Error())
	}

	return responses.OK(c, doc)
}