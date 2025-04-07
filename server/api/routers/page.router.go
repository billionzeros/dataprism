package routers

import (
	"context"

	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/gofiber/fiber/v3"
	"go.uber.org/zap"
)

// DocumentRouter handles the routing for document-related endpoints.
type PageRouter struct {
	ctx context.Context
	router fiber.Router

	*zap.Logger
}

// NewPageRouter creates a new DocumentRouter instance with the provided fiber.Router.
func AddPageRouter(ctx context.Context, baseRouter *fiber.Router) *PageRouter {
	router := &PageRouter{
		ctx: context.WithoutCancel(ctx),
		router: (*baseRouter).Group("/document"),
		Logger: logger.FromCtx(ctx),
	}

	router.registerRoutes()

	return router
}

// registerRoutes registers the routes for the DocumentRouter.
func (d *PageRouter) registerRoutes() {
	d.router.Post("/create", d.createDocument)
}

// createDocument handles the creation of a document.
func (d *PageRouter) createDocument(c fiber.Ctx) error {
	d.Sugar().Info("Creating document")

	return c.JSON(fiber.Map{
		"message": "Document created successfully",
	})
}