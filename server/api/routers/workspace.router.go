package routers

import (
	"context"

	"github.com/OmGuptaIND/shooting-star/api/responses"
	"github.com/OmGuptaIND/shooting-star/api/schema"
	"github.com/OmGuptaIND/shooting-star/appError"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/db/models"
	service "github.com/OmGuptaIND/shooting-star/services/workspace"
	"github.com/gofiber/fiber/v3"
	"go.uber.org/zap"
)

// DocumentRouter handles the routing for document-related endpoints.
type router struct {
	ctx context.Context
	workspaceService service.WorkspaceService
	logger *zap.Logger
}

// NewDocumentRouter creates a new DocumentRouter instance with the provided fiber.Router.
func RegisterWorkspaceRouter(ctx context.Context, baseRouter fiber.Router) {
	handler := &router{
		ctx: ctx,
		workspaceService: service.New(ctx),
		logger: logger.FromCtx(ctx),
	}

	// Grouping the routes under `/documents`
	group := baseRouter.Group("/workspace")

	group.Post("/create", handler.createWorkspace) // Upload a CSV file
}

func (r *router) createWorkspace(c fiber.Ctx) error {
	req := new(schema.CreateWorkspaceRequest)

	if err := c.Bind().Body(&req); err != nil {
		r.logger.Error("Error binding request body", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, "Invalid request body")
	}

	if req.Name == "" {
		r.logger.Error("Invalid request parameters", zap.String("name", req.Name))
		return responses.BadRequest(c, appError.InternalError, "Name is required")
	}

	r.logger.Info("Received Workspace creation request", zap.String("name", req.Name))

	workspace := &models.Workspace{
		Name: req.Name,
		Description: req.Description,
	}

	workspaceDetails, err := r.workspaceService.CreateWorkspace(workspace)
	if err != nil {
		r.logger.Error("Error creating workspace", zap.Error(err))
		return responses.BadRequest(c, appError.InternalError, "Failed to create workspace")
	}

	response := &schema.CreateWorkspaceResponse{
		WorkspaceId: workspaceDetails.ID,
		Workspace: workspaceDetails,
	}

	return responses.OK(c, response)
}