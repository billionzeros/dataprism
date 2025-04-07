# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands
- `make run` - Run the application
- `make build` - Build the application binary
- `make start` - Build and run the application
- `go test ./... -v` - Run all tests
- `go test ./path/to/package -v` - Run tests for a specific package
- `go test ./path/to/package -run TestName -v` - Run a specific test
- `golangci-lint run` - Run linters

## Database Commands
- `make create <migration_name>` - Create a new migration
- `make migrate-up` - Apply all migrations
- `make migrate-down` - Rollback last migration
- `make migrate-upto <version>` - Apply migrations up to specific version

## Code Style Guidelines
- Imports: Group standard library, external packages, and internal packages
- Error handling: Use custom AppError interface from appError package
- Logging: Use zap.Logger injected via context
- Naming: CamelCase for exported, camelCase for unexported
- Types: Use strong typing with descriptive custom types
- Comments: Document all exported functions, types, and constants
- File structure: Follow standard Go project layout
- GORM: Use hooks for consistent database validations
- Dont add unnecessary comments, use comments only when necessary