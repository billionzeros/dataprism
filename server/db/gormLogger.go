package db

import (
	"context"
	"errors"
	"fmt"
	"time"

	"go.uber.org/zap"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// GormLogger implements GORM's logger.Interface
type GormLogger struct {
	logger *zap.Logger
}

// NewGormLogger creates a new GORM logger that uses zap
func NewGormLogger(zapLogger *zap.Logger) logger.Interface {
	return &GormLogger{
		logger: zapLogger,
	}
}

// LogMode implements logger.Interface
func (l *GormLogger) LogMode(level logger.LogLevel) logger.Interface {
	return l
}

// Info implements logger.Interface
func (l *GormLogger) Info(ctx context.Context, msg string, data ...interface{}) {
	l.logger.Info(fmt.Sprintf(msg, data...))
}

// Warn implements logger.Interface
func (l *GormLogger) Warn(ctx context.Context, msg string, data ...interface{}) {
	l.logger.Warn(fmt.Sprintf(msg, data...))
}

// Error implements logger.Interface
func (l *GormLogger) Error(ctx context.Context, msg string, data ...interface{}) {
	l.logger.Error(fmt.Sprintf(msg, data...))
}

// Trace implements logger.Interface
func (l *GormLogger) Trace(ctx context.Context, begin time.Time, fc func() (sql string, rowsAffected int64), err error) {
	elapsed := time.Since(begin)
	sql, rows := fc()

	fields := []zap.Field{
		zap.Duration("elapsed", elapsed),
		zap.String("sql", sql),
		zap.Int64("rows", rows),
	}

	if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
		fields = append(fields, zap.Error(err))
		l.logger.Error("sql-trace", fields...)
		l.logger.Error("Error", zap.Error(err))

		return
	}

	if elapsed > 1*time.Second {
		l.logger.Debug("sql-trace-slow-query", fields...)
		return
	}
}
