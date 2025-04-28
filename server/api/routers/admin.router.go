package routers

import (
	"context"
	"fmt"

	"github.com/OmGuptaIND/shooting-star/api/responses"
	"github.com/OmGuptaIND/shooting-star/api/schema"
	"github.com/OmGuptaIND/shooting-star/appError"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	uploadService "github.com/OmGuptaIND/shooting-star/services/upload"
	"github.com/gofiber/fiber/v3"
	"go.uber.org/zap"
)

// AdminRouter handles the routing for document-related endpoints.
type AdminRouter struct {
	ctx context.Context
	logger *zap.Logger
}

// RegisterAdminRouter creates a new AdminRouter instance with the provided fiber.Router.
func RegisterAdminRouter(ctx context.Context, baseRouter fiber.Router) {
	handler := &AdminRouter{
		ctx: ctx,
		logger: logger.FromCtx(ctx),
	}

	// Grouping the routes under `/documents`
	apiGroup := baseRouter.Group("/admin")

	apiGroup.Post("/build-mock", handler.buildMockDB) // build the DB with mock data.
}

func (d *AdminRouter) buildMockDB(c fiber.Ctx) error {
	req := new(schema.BuildMockRequest)

	if err := c.Bind().Body(req); err != nil {
		return responses.BadRequest(c, appError.InternalError, "Invalid request body")
	}

	if req.WorkspaceID == "" {
		d.logger.Error("Invalid request parameters", zap.String("workspaceId", req.WorkspaceID))
		return responses.BadRequest(c, appError.BadRequest, "Workspace ID is required")
	}

	basePath := `/Users/omg/Desktop/01/shooting-star/server/mock/%s.csv`
	mockDataInfo := []struct {
		FileName string
		FilePath string
		Description string
	}{
		{
			FileName:   "mock_file_1",
			FilePath: fmt.Sprintf(basePath, "mock_file_1"),
			Description: "Seller Information, Including there City and States with ZIP Codes",
		},
		{
			FileName:   "mock_file_2",
			FilePath: fmt.Sprintf(basePath, "mock_file_2"),
			Description: "Product Details, and Information",
		},
		{
			FileName:   "mock_file_3",
			FilePath: fmt.Sprintf(basePath, "mock_file_3"),
			Description: "Order Details, With there Order Details and Status",
		},
		{
			FileName:   "mock_file_4",
			FilePath: fmt.Sprintf(basePath, "mock_file_4"),
			Description: "Customer Details, Including there City and States with ZIP Codes",
		},
		{
			FileName:   "mock_file_5",
			FilePath: fmt.Sprintf(basePath, "mock_file_5"),
			Description: "Geolocation Details, of all the zip codes",
		},
		{
			FileName:   "mock_file_6",
			FilePath: fmt.Sprintf(basePath, "mock_file_6"),
			Description: "Order Details, majorly about the seller",
		},
		{
			FileName:   "mock_file_7",
			FilePath: fmt.Sprintf(basePath, "mock_file_7"),
			Description: "Order Details, and there Payment Methods etc",
		},
		{
			FileName:   "mock_file_8",
			FilePath: fmt.Sprintf(basePath, "mock_file_8"),
			Description: "Product Reviews and there associated comments",
		},
	}

	queuedCount := 0
    errorCount := 0
    var submissionErrors []string

	for _, mockData := range mockDataInfo {
		err := uploadService.Service.QueueCsvUpload(&uploadService.QueueCsvDetails{
			FileName:  mockData.FileName,
			FilePath: mockData.FilePath,
			WorkspaceID: req.WorkspaceID,
			Description: mockData.Description,
		})

		if err != nil {
            errorCount++
            errMsg := fmt.Sprintf("Failed to queue %s: %v", mockData.FileName, err)
            submissionErrors = append(submissionErrors, errMsg)
            d.logger.Error("Error submitting mock file to queue", zap.String("fileName", mockData.FileName), zap.Error(err))
        } else {
            queuedCount++
            d.logger.Info("Successfully queued mock file", zap.String("fileName", mockData.FileName))
        }
	}

	resp := &schema.BuildMockResponse{
		Message: fmt.Sprintf("Queued %d files successfully", queuedCount),
		FilesQueued: queuedCount,
		ErrorCount: errorCount,
	}

	if errorCount > 0 {
		resp.ErrorDetails = submissionErrors
		return responses.StatusMultiStatus(c, resp)
	}

	return responses.Created(c, resp)
}