-- +goose Up
CREATE TABLE vector_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

CREATE INDEX idx_vector_embeddings_deleted_at ON vector_embeddings(deleted_at);

-- +goose Down
DROP INDEX IF EXISTS idx_vector_embeddings_deleted_at;
DROP TABLE IF EXISTS vector_embeddings;