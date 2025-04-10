# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Server (Go) Commands
- `make run` - Run the application
- `make build` - Build the application binary
- `make dev` - Run the application with hot reload using Air
- `make start` - Build and run the application
- `go test ./... -v` - Run all tests
- `go test ./path/to/package -v` - Run tests for a specific package
- `go test ./path/to/package -run TestName -v` - Run a specific test
- `golangci-lint run` - Run linters

## Client (Next.js) Commands
- `npm run dev` - Run development server with Turbo
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Run ESLint with auto-fix
- `npm run typecheck` - Type check with TypeScript
- `npm run check` - Run lint and type check
- `npm run build` - Build for production

## Code Style Guidelines
### Server (Go)
- Imports: Group standard library, external packages, and internal packages
- Error handling: Use custom AppError interface from appError package
- Logging: Use zap.Logger injected via context
- Naming: CamelCase for exported, camelCase for unexported
- Types: Use strong typing with descriptive custom types
- File structure: Follow standard Go project layout
- GORM: Use hooks for consistent database validations

### Client (Next.js)
- Formatting: Uses Biome with tabs and double quotes
- State management: Jotai for global state
- Component structure: Follows component/UI pattern
- CSS: Tailwind with class-variance-authority
- Forms/Validation: Zod schemas
- API: tRPC for type-safe APIs

Don't add unnecessary comments, use comments only when necessary