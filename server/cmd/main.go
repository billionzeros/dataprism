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

	// Create and start the API server
	server := api.NewApiServer(ctx)
	
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