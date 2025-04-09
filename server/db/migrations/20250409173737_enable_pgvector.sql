-- +goose Up
-- Enables the pgvector extension if it doesn't already exist.
CREATE EXTENSION IF NOT EXISTS vector;

-- +goose Down
-- DROP EXTENSION IF EXISTS vector;
-- It's often safer to leave the Down section empty or comment out the DROP for extensions.