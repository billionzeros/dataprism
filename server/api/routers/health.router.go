package routers

import (
	"context"

	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/gofiber/fiber/v3"
	"go.uber.org/zap"
)

// DocumentRouter handles the routing for document-related endpoints.
type HealthRouter struct {
	ctx context.Context
	router fiber.Router

	*zap.Logger
}

// NewPageRouter creates a new DocumentRouter instance with the provided fiber.Router.
func AddHealthRouter(ctx context.Context, baseRouter *fiber.Router) *HealthRouter {
	router := &HealthRouter{
		ctx: context.WithoutCancel(ctx),
		router: (*baseRouter).Group("/healthz"),
		Logger: logger.FromCtx(ctx),
	}

	router.registerRoutes()

	return router
}

// registerRoutes registers the routes for the DocumentRouter.
func (d *HealthRouter) registerRoutes() {
	d.router.Get("/ping", d.ping)
}

// createDocument handles the creation of a document.
func (d *HealthRouter) ping(c fiber.Ctx) error {
	return c.JSON(fiber.Map{
		"message": "Pong",
	})
}