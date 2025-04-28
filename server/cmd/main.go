package main

import (
	"context"
	"flag"
	"os"
	"os/signal"
	"sync"
	"syscall"

	"github.com/OmGuptaIND/shooting-star/api"
	"github.com/OmGuptaIND/shooting-star/config/env"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	"github.com/OmGuptaIND/shooting-star/db"
	uploadService "github.com/OmGuptaIND/shooting-star/services/upload"
	"go.uber.org/zap"
)

func main() {
	envFile := flag.String("env", ".env", "Environment file")
	flag.Parse()

	_, err := env.LoadEnvironmentVariables(*envFile)
	if err != nil {
		panic(err)
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Create a Logger Instance
	l, ctx := logger.New(ctx, logger.LoggerOpts{
		Level: "info",
		AxiomConfig: &logger.AxiomConfig{
			Token:   env.GetAxiomToken(),
			OrgId:   env.GetAxiomOrgID(),
			DataSet: env.GetAxiomDataSet(),
		},
	})
	defer l.Sync()

	// Establish a connection to the database
	conn, err := db.NewDBConnection(ctx)
	if err != nil {
		l.Error("Failed to connect to database", zap.Error(err))
		panic(err)
	}

	if err := conn.Health(); err != nil {
		l.Error("Database health check failed", zap.Error(err))
		panic(err)
	}

	// Create Required Services.
	uploadService := uploadService.New(ctx) // Upload service instance
	defer uploadService.Close()
	
	// Create and start the API server
	server := api.NewApiServer(ctx)

	// Setup Context cancellation and signal handling
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	
	var wg sync.WaitGroup
	
	wg.Add(1)
	go func() {
		defer wg.Done()
		listenAddr := env.GetListenAddr()

		if err := server.Listen(listenAddr); err != nil {
			l.Error("Server error", zap.Error(err))
			cancel()
		}
	}()
	
	wg.Add(1)
	go func() {
		defer wg.Done()

		select {
			case <-ctx.Done():
				l.Info("Context cancelled, shutting down")

			case <-sigChan:
				l.Info("Received signal, shutting down services", zap.String("signal", "SIGINT/SIGTERM"))
				cancel()
			}
	}()
	
	wg.Wait()
}