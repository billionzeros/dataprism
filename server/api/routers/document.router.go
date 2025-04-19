package routers

import (
	"context"
	"errors"

	"github.com/OmGuptaIND/shooting-star/api/responses"
	"github.com/OmGuptaIND/shooting-star/api/schema"
	"github.com/OmGuptaIND/shooting-star/appError"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/db/models"
	documentservice "github.com/OmGuptaIND/shooting-star/services/document"
	"github.com/gofiber/fiber/v3"
	"go.uber.org/zap"
	"gorm.io/gorm"
)

// DocumentRouter handles the routing for document-related endpoints.
type DocumentRouter struct {
	ctx context.Context
	documentService documentservice.DocumentService

	logger *zap.Logger
}

// NewDocumentRouter creates a new DocumentRouter instance with the provided fiber.Router.
func RegisterDocumentRoutes(ctx context.Context, baseRouter fiber.Router) {
	handler := &DocumentRouter{
		ctx: ctx,
		documentService: documentservice.New(ctx),
		logger: logger.FromCtx(ctx),
	}

	// Grouping the routes under `/documents`
	documentGroup := baseRouter.Group("/documents")

	documentGroup.Post("/create", handler.createDocument) // Create a new document
	documentGroup.Get("/:id", handler.getDocumentById) // Get a document by ID
}

// createDocument handles the creation of a new document.
func (d *DocumentRouter) createDocument(c fiber.Ctx) error {
	req := new(schema.CreateDocumentRequest)

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

	d.logger.Info("New Document created", zap.String("title", req.Title))

	response := &schema.CreateDocumentResponse{
		DocumentID: doc.ID,
		Document: doc,
	}

	return responses.Created(c, response)
}

// getDocumentById handles the retrieval of a document by its ID.
func (d *DocumentRouter) getDocumentById(c fiber.Ctx) error {
	req := new(schema.GetDocumentByIDRequest)

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

	response := &schema.GetDocumentByIDResponse{
		DocumentID: doc.ID,
		Title: doc.Title,
	}

	return responses.OK(c, response)
}