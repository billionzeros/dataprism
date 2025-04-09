package api

import (
	"context"
	"net"

	"github.com/OmGuptaIND/shooting-star/api/routers"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/gofiber/fiber/v3"
	"go.uber.org/zap"
)

// ApiServer represents the API server using which the application will be served.
type ApiServer struct {
	ctx context.Context
	app *fiber.App


	*zap.Logger
}

// NewApiServer creates a new ApiServer instance with the provided context and logger.
func NewApiServer(ctx context.Context) *ApiServer {
	app := fiber.New(fiber.Config{
		ServerHeader: "Prism",
		AppName: "Prism",
		ErrorHandler: errorHandler,
		ReadTimeout: 0,
	})

	apiServer := &ApiServer{
		ctx: ctx,
		app: app,
		Logger: logger.FromCtx(ctx),
	}

	// BaseRouter for API versioning
	baseRouter := app.Group("/api/v1")

	// Registering routers
	routers.AddDocumentRouter(ctx, &baseRouter) // Page Router handles document-related endpoints
	routers.AddHealthRouter(ctx, &baseRouter) // Health Router handles health check endpoints

	apiServer.app.Use(apiServer.notFoundHandler)

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
			a.Logger.Error("Error shutting down the server: %v\n", zap.String("error", err.Error()))
		},
		OnShutdownSuccess: func() {
			a.Logger.Info("API Server shutdown successfully")
		},
		ListenerAddrFunc: func(net.Addr) {
			a.Logger.Info("ApiServer listening: ", zap.String("Addr", addr))
		},
	})
}

// `notFoundHandler` handles unmatched routes.
func (a *ApiServer) notFoundHandler(c fiber.Ctx) error {
	a.Sugar().Info("Not Found: %s", c)

	return fiber.NewError(fiber.StatusNotFound, "Resource not found")
}

// `handleContextClose` handles the context cancellation and shuts down the server.
func (a *ApiServer) handleContextClose() {
	<-a.ctx.Done()

	if err := a.app.Shutdown(); err != nil {
		a.Logger.Error("Error shutting down the server: %v\n", zap.String("error", err.Error()))
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