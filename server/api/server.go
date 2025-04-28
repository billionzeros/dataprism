package api

import (
	"context"
	"net"
	"time"

	"github.com/OmGuptaIND/shooting-star/api/routers"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/gofiber/fiber/v3"
	"github.com/gofiber/fiber/v3/middleware/cors"
	"github.com/gofiber/fiber/v3/middleware/healthcheck"
	"github.com/gofiber/fiber/v3/middleware/helmet"
	"github.com/gofiber/fiber/v3/middleware/idempotency"
	"github.com/gofiber/fiber/v3/middleware/limiter"
	recoverer "github.com/gofiber/fiber/v3/middleware/recover"
	"go.uber.org/zap"
)

// ApiServer represents the API server using which the application will be served.
type ApiServer struct {
	ctx context.Context
	app *fiber.App

	logger *zap.Logger
}

// NewApiServer creates a new ApiServer instance with the provided context and logger.
func NewApiServer(ctx context.Context) *ApiServer {
	app := fiber.New(fiber.Config{
		ServerHeader: "Prism",
		AppName: "Prism",
		ErrorHandler: errorHandler,
		ReadTimeout: 0,
	})

	// Middleware to recover from panics
	app.Use(recoverer.New())

	// Middleware to handle CORS
	app.Use(cors.New())

	// Middleware to set security headers
	app.Use(helmet.New())

	// This middleware is used to prevent duplicate requests from being processed.
	app.Use(idempotency.New())

	// Middleware to limit the number of requests from a single IP address
	app.Use(limiter.New(limiter.Config{
		Max:            20,
		Expiration:     30 * time.Second,
		LimiterMiddleware: limiter.SlidingWindow{},
	}))

	// Middleware to handle Liveness and Readiness check for the API server
	app.Get(healthcheck.DefaultLivenessEndpoint, healthcheck.NewHealthChecker())

	apiServer := &ApiServer{
		ctx: ctx,
		app: app,
		logger: logger.FromCtx(ctx),
	}

	// BaseRouter for API versioning
	apiV1 := app.Group("/api/v1")

	// Registering routers
	routers.RegisterAdminRouter(ctx, apiV1) // Admin Router handles admin-related endpoints
	routers.RegisterDocumentRoutes(ctx, apiV1) // Page Router handles document-related endpoints
	routers.RegisterUploadRouter(ctx, apiV1) // Upload Router handles upload-related endpoints
	routers.RegisterWorkspaceRouter(ctx, apiV1) // Workspace Router handles workspace-related endpoints
	routers.RegisterChatRoutes(ctx, apiV1) // Chat Router handles chat-related endpoints
	

	// Middleware to handle not found routes, this should be the last middleware in the chain.
	app.Use(apiServer.notFoundHandler)

	go apiServer.handleContextClose()

	return apiServer
}

// Listen starts the API server and listens for incoming requests.
func (a *ApiServer) Listen(addr string) error {	
	return a.app.Listen(addr, fiber.ListenConfig{
		GracefulContext:	  a.ctx,
		EnablePrintRoutes: false,
		EnablePrefork: 	false, // Allows Running multiple instances for the API Server.
		DisableStartupMessage: true,
		OnShutdownError: func(err error) {
			a.logger.Error("Error shutting down the server: %v\n", zap.String("error", err.Error()))
		},
		OnShutdownSuccess: func() {
			a.logger.Info("API Server shutdown successfully")
		},
		ListenerAddrFunc: func(net.Addr) {
			a.logger.Info("ApiServer listening: ", zap.String("Addr", addr))
		},
	})
}

// `notFoundHandler` handles unmatched routes.
func (a *ApiServer) notFoundHandler(c fiber.Ctx) error {
	a.logger.Sugar().Info("Not Found: %s", c)

	return fiber.NewError(fiber.StatusNotFound, "Resource not found")
}

// `handleContextClose` handles the context cancellation and shuts down the server.
func (a *ApiServer) handleContextClose() {
	<-a.ctx.Done()

	if err := a.app.Shutdown(); err != nil {
		a.logger.Error("Error shutting down the server: %v\n", zap.String("error", err.Error()))
	}
}


// errorHandler handles all internal server errors.
func errorHandler(c fiber.Ctx, err error) error {
	code := fiber.StatusInternalServerError
	msg := "Internal Server Error"
	if e, ok := err.(*fiber.Error); ok {
		code = e.Code
		msg = e.Message
	}
	c.Set(fiber.HeaderContentType, fiber.MIMETextPlainCharsetUTF8)
	zap.L().Error("Error %d: %s\n", zap.Int("code", code), zap.String("message", msg))

	return c.Status(code).SendString(msg)
}