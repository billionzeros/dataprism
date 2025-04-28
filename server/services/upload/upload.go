package uploadService

import (
	"context"

	"github.com/OmGuptaIND/shooting-star/appError"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	csvService "github.com/OmGuptaIND/shooting-star/services/csv"
	workspaceService "github.com/OmGuptaIND/shooting-star/services/workspace"
	"github.com/panjf2000/ants/v2"
	"go.uber.org/zap"
)


var Service *service

type service struct {
	ctx context.Context
	cancelFunc context.CancelFunc

	workerPool *ants.Pool

	logger *zap.Logger
}

// New creates a new instance of DocumentService with the provided logger.
func New(ctx context.Context) *service {
	if Service != nil {
		return Service
	}

	log := logger.FromCtx(ctx)

	// Initialize the worker pool with a size of 10
	pool, err := ants.NewPool(10, ants.WithMaxBlockingTasks(100), ants.WithPanicHandler(func(err interface{}) {
        log.Error("Worker panic recovered", zap.Any("error", err))
    }))
    if err != nil {
        log.Fatal("Failed to create worker pool", zap.Error(err)) // Fatal if pool creation fails
    }

	ctx, cancel := context.WithCancel(ctx)
	uploadService := &service{
		ctx: ctx,
		cancelFunc: cancel,

		workerPool: pool,
		logger: logger.FromCtx(ctx),
	}

	Service = uploadService // Assign the instance to the global variable

	return Service
}

// Close releases any resources held by the DocumentService.
func (s *service) Close() {
	s.logger.Info("Closing upload service")
	s.cancelFunc() // Cancel the context to stop any ongoing operations

	s.workerPool.Release() // Release the worker pool
}

// QueueCsvUpload is an asynchronous function that queues a CSV file for processing and further uploading
func (s *service) QueueCsvUpload(details *QueueCsvDetails) (error) {
	s.logger.Info("Queueing CSV for processing", zap.String("fileName", details.FileName))

	task := func () {
		_, err := s.processCsv(details)
		if err != nil {
			s.logger.Error("Background task failed", zap.Error(err))
		}

		s.logger.Info("CSV processing completed", zap.String("fileName", details.FileName))
	}

	err := s.workerPool.Submit(task)
	if err != nil {
		s.logger.Error("Failed to submit task to worker pool", zap.Error(err))
		return appError.New(appError.InternalError, err.Error(), err)
	}

	return nil
}

// ProcessCSV is a synchronous function that processes a CSV file.
func (s *service) processCsv(details *QueueCsvDetails) (*csvService.CSVDetails, error) {
	s.logger.Info("Processing CSV file", zap.String("fileName", details.FileName))

	workspaceService := workspaceService.New(s.ctx)
	defer workspaceService.Close()

	workspaceId := details.WorkspaceID
	if workspaceId == "" {
		s.logger.Error("Invalid request parameters", zap.String("workspaceId", workspaceId))
		return nil, appError.New(appError.BadRequest, "Workspace ID is required", nil)
	}

	workSpaceDetails, err := workspaceService.GetWorkspaceById(details.WorkspaceID)
	if err != nil {
		s.logger.Error("Error fetching workspace details", zap.Error(err))
		return nil, appError.New(appError.InternalError, "Failed to fetch workspace details", err)
	}

	s.logger.Info("Received CSV upload request", zap.String("fileName", details.FileName))


	csvHandler := csvService.New(s.ctx)
	defer csvHandler.Close()

	csvDetails, err := csvHandler.ExtractCSVDetails(details.FilePath)
	if err != nil {
		s.logger.Error("Error extracting CSV details", zap.Error(err))
		return nil, appError.New(appError.InternalError, "Failed to extract CSV details", err)
	}

	uploadInfo, err := csvHandler.UploadCSV(workSpaceDetails, csvDetails)
	if err != nil {
		s.logger.Error("Error uploading CSV file", zap.Error(err))
		return nil, appError.New(appError.InternalError, "Failed to upload CSV file", err)
	}

	// Set the upload information in the CSV details
	csvDetails.UploadInfo = uploadInfo

	err = csvHandler.ProcessAndEmbedCSV(csvDetails)
	if err != nil {
		s.logger.Error("Error processing CSV file", zap.Error(err))
		return nil, appError.New(appError.InternalError, "Failed to process CSV file", err)
	}
	
	return csvDetails, nil
}