package main

import (
	"context"
	"flag"

	"github.com/OmGuptaIND/shooting-star/config/env"
	"github.com/OmGuptaIND/shooting-star/config/logger"
)

func main()  {
	// Load environment variables
	_, err := env.LoadEnvironmentVariables(*flag.String("env", ".env", "Environment file"))
	if err != nil {
		panic(err)
	}

	// Create a global context
	globalCtx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Create a Logger Instance
	l := logger.New(globalCtx, logger.LoggerOpts{
		Level: "info",
		AxiomConfig: &logger.AxiomConfig{
			Token:   env.GetAxiomToken(),
			OrgId:   env.GetAxiomOrgID(),
			DataSet: env.GetAxiomDataSet(),
		},
	})
	defer l.Sync() // Flushes Buffer, when the application is getting closed


	l.Info("Server started")
}