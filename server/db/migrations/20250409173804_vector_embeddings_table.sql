-- +goose Up
CREATE TABLE vector_embeddings (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL, -- If using GORM's soft delete

    -- Metadata columns
    source_type TEXT NOT NULL,
    source_identifier TEXT NOT NULL,
    related_id TEXT NULL,
    column_or_chunk_name TEXT NULL,
    original_text TEXT NULL,

    embedding vector(768) NOT NULL
);


-- +goose Down
DROP TRIGGER IF EXISTS set_timestamp ON vector_embeddings;
DROP FUNCTION IF EXISTS trigger_set_timestamp();
DROP TABLE IF EXISTS vector_embeddings;