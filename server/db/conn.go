package db

import (
	"context"
	"time"

	"github.com/OmGuptaIND/shooting-star/appError"
	"github.com/OmGuptaIND/shooting-star/config/env"
	"github.com/OmGuptaIND/shooting-star/config/logger"
	"go.uber.org/zap"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/schema"
)

var Conn DBConnection

type Config struct {
	MaxOpenConns    int
	MaxIdleConns    int
	ConnMaxLifetime time.Duration
	ConnMaxIdleTime time.Duration
}

type DBConnection struct {
	ctx    context.Context
	logger *zap.Logger
	*gorm.DB
}

// DefaultConfig returns the default database configuration
func DefaultConfig() Config {
	return Config{
		MaxOpenConns:    25,
		MaxIdleConns:    10,
		ConnMaxLifetime: time.Hour,
		ConnMaxIdleTime: 10 * time.Minute,
	}
}

// NewDBConnection creates a new database connection
func NewDBConnection(ctx context.Context) (*DBConnection, error) {
	dbCtx := context.WithoutCancel(ctx)

	logger := logger.FromCtx(dbCtx)

	config := DefaultConfig()

	pgCnn := postgres.New(
		postgres.Config{
			DSN:                  env.GetDatabaseURL(),
			PreferSimpleProtocol: true,
		},
	)

	gormConfig := &gorm.Config{
		PrepareStmt: true,
		NamingStrategy: schema.NamingStrategy{
			SingularTable: true,
		},
		Logger: NewGormLogger(logger),
	}

	db, err := gorm.Open(pgCnn, gormConfig)

	if err != nil {
		return nil, appError.New(appError.InternalError, "failed to connect to database", err)
	}

	sqlDB, err := db.DB()

	if err != nil {
		return nil, appError.New(appError.InternalError, "failed to get database connection", err)
	}

	sqlDB.SetMaxOpenConns(config.MaxOpenConns)
	sqlDB.SetMaxIdleConns(config.MaxIdleConns)
	sqlDB.SetConnMaxLifetime(config.ConnMaxLifetime)
	sqlDB.SetConnMaxIdleTime(config.ConnMaxIdleTime)

	if err := sqlDB.Ping(); err != nil {
		return nil, appError.New(appError.InternalError, "failed to ping database", err)
	}

	logger.Info("Successfully connected to database",
		zap.Int("maxOpenConns", config.MaxOpenConns),
		zap.Int("maxIdleConns", config.MaxIdleConns),
		zap.Duration("connMaxLifetime", config.ConnMaxLifetime),
	)

	Conn = DBConnection{
		ctx:    dbCtx,
		DB:     db,
		logger: logger,
	}

	return &Conn, nil
}

// Close closes the database connection
func (d *DBConnection) Close() error {
	sqlDB, err := d.DB.DB()
	if err != nil {
		return appError.New(appError.InternalError, "failed to get database connection", err)
	}

	if err := sqlDB.Close(); err != nil {
		return appError.New(appError.InternalError, "failed to close database connection", err)
	}

	d.logger.Info("Database connection closed")

	return nil
}

// Health checks the database connection health
func (d *DBConnection) Health() error {
	sqlDB, err := d.DB.DB()
	if err != nil {
		return appError.New(appError.InternalError, "failed to get database connection", err)
	}

	if err := sqlDB.Ping(); err != nil {
		return appError.New(appError.InternalError, "failed to ping database", err)
	}

	return nil
}
