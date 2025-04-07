package logger

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/OmGuptaIND/shooting-star/config"
	"github.com/OmGuptaIND/shooting-star/config/env"
	adapter "github.com/axiomhq/axiom-go/adapters/zap"
	"github.com/axiomhq/axiom-go/axiom"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

type AxiomConfig struct {
	Token   string
	OrgId   string
	DataSet string
}

type LoggerOpts struct {
	Level       string
	AxiomConfig *AxiomConfig
}

// validateAxiomConfig validates the Axiom configuration
func validateAxiomConfig(cfg *AxiomConfig) error {
	if cfg == nil {
		return fmt.Errorf("axiom config is nil")
	}
	if cfg.Token == "" {
		return fmt.Errorf("axiom token is empty")
	}
	if cfg.OrgId == "" {
		return fmt.Errorf("axiom org id is empty")
	}
	if cfg.DataSet == "" {
		return fmt.Errorf("axiom dataset is empty")
	}
	return nil
}

// FromCtx returns the logger from the context
func FromCtx(ctx context.Context) *zap.Logger {
	logger := ctx.Value(config.LoggerCtxKey).(*zap.Logger)

	return logger
}

// WithCtx adds the logger to the context
func WithCtx(ctx context.Context, logger *zap.Logger) context.Context {
	return context.WithValue(ctx, config.LoggerCtxKey, logger)
}

// BuildZapLogger builds a new zap logger
func buildZapLogger(opts LoggerOpts) (*zap.Logger, error) {
	level := parseLoggerLevel(opts.Level)

	encoderConfig := getEncoderConfig()

	config := zap.Config{
		Level:             zap.NewAtomicLevelAt(*level),
		Development:       env.IsDevelopment(),
		DisableCaller:     false,
		DisableStacktrace: false,
		Sampling:          nil,
		Encoding:          "console",
		EncoderConfig:     *encoderConfig,
		OutputPaths: []string{
			"stderr",
		},
		ErrorOutputPaths: []string{
			"stderr",
		},
	}

	return config.Build()
}

// buildAxiomCore builds a new axiom core
func buildAxiomCore(opts LoggerOpts) (*zapcore.Core, error) {
	if err := validateAxiomConfig(opts.AxiomConfig); err != nil {
		return nil, fmt.Errorf("invalid axiom config: %w", err)
	}

	clientOpts := []axiom.Option{
		axiom.SetPersonalTokenConfig(opts.AxiomConfig.Token, opts.AxiomConfig.OrgId),
	}

	axiomClient, err := axiom.NewClient(
		clientOpts...,
	)

	if err != nil {
		return nil, err
	}

	adapterOpts := []adapter.Option{
		adapter.SetClient(axiomClient),
		adapter.SetDataset(opts.AxiomConfig.DataSet),
	}

	axiomCore, err := adapter.New(
		adapterOpts...,
	)

	if err != nil {
		return nil, err
	}

	return &axiomCore, nil
}

// New creates a new logger
func New(ctx context.Context, opts LoggerOpts) (*zap.Logger, context.Context) {
	isDevelopment := env.IsDevelopment()

	baseLogger, err := buildZapLogger(opts)

	if err != nil {
		log.Panic("Failed to build logger: ", err)
	}

	if isDevelopment {
		return baseLogger, WithCtx(ctx, baseLogger)
	}

	if opts.AxiomConfig == nil {
		log.Panic("Axiom config is missing, Stopping the Service")
	}

	axiomCore, err := buildAxiomCore(opts)

	if err != nil {
		log.Panic("Failed to build Axiom logger: ", err)
	}

	combinedCores := zapcore.NewTee(
		baseLogger.Core(),
		*axiomCore,
	)

	go func() {
		for {
			timer := time.NewTimer(5 * time.Second)

			select {
			case <-timer.C:
				syncErr := (*axiomCore).Sync()
				if syncErr != nil {
					log.Panic("Failed to sync logs: ", syncErr)
				}

			case <-ctx.Done():
				timer.Stop()

				syncErr := (*axiomCore).Sync()
				if syncErr != nil {
					log.Panic("Failed to sync logs: ", syncErr)
				}

				return
			}

			timer.Stop()
		}

	}()

	logger := zap.New(combinedCores, zap.AddCaller(), zap.AddStacktrace(zapcore.ErrorLevel))

	zap.ReplaceGlobals(logger)

	return logger, WithCtx(ctx, logger)

}

// parseLoggerLevel parses the string level to zapcore.Level
func parseLoggerLevel(level string) *zapcore.Level {
	l, err := zapcore.ParseLevel(level)

	if err != nil {
		log.Panic("Invalid log level, Stopping the Service, Reason: ", err)
	}

	return &l
}

// getEncoderConfig returns the encoder config
func getEncoderConfig() *zapcore.EncoderConfig {
	isDevelopment := env.IsDevelopment()

	encoderConfig := zap.NewDevelopmentEncoderConfig()

	if !isDevelopment {
		encoderConfig = zap.NewProductionEncoderConfig()
	}

	encoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

	encoderConfig.TimeKey = "timestamp"

	return &encoderConfig
}
