run:
	@echo "Running $(APP_NAME)..."
	@go run cmd/*.go $(filter-out $@,$(MAKECMDGOALS))

build:
	@go build -v -o ./bin/main cmd/*.go

dev:
	@air

start:
	@echo "Starting $(APP_NAME)..."

	@echo "Building the Project..."

	@go build -o bin/main cmd/*.go

	@echo "Running the Project..."

	@./bin/main

# Database Related Commands
create:
	@goose  create $(filter-out $@,$(MAKECMDGOALS)) sql -env .env -dir db/migrations

migrate-up:
	@goose up postgres -env .env -dir db/migrations

migrate-down:
	@goose down postgres -env .env -dir db/migrations

migrate-down-all:
	@goose down-to 0 postgres -env .env -dir db/migrations

migrate-upto:
	@goose up-to $(filter-out $@,$(MAKECMDGOALS)) postgres -env .env -dir db/migrations

.PHONY: run build create migrate-up migrate-down migrate-upto gen-reward-calculator

%:
	@:

