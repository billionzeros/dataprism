package routers

import (
	"context"

	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/gofiber/fiber/v3"
	"go.uber.org/zap"
)

// DocumentRouter handles the routing for document-related endpoints.
type DocumentRouter struct {
	ctx context.Context
	router fiber.Router

	*zap.Logger
}

// NewDocumentRouter creates a new DocumentRouter instance with the provided fiber.Router.
func AddDocumentRouter(ctx context.Context, baseRouter *fiber.Router) *DocumentRouter {
	router := &DocumentRouter{
		ctx: context.WithoutCancel(ctx),
		router: (*baseRouter).Group("/document"),
		Logger: logger.FromCtx(ctx),
	}

	router.registerRoutes()

	return router
}

// registerRoutes registers the routes for the DocumentRouter.
func (d *DocumentRouter) registerRoutes() {
	d.router.Post("/create", d.createDocument)
}

// createDocument handles the creation of a document.
func (d *DocumentRouter) createDocument(c fiber.Ctx) error {
	d.Info("Creating A New Document", zap.String("path", c.Path()))
	
	

	return c.JSON(fiber.Map{
		"message": "Document created successfully",
	})
}