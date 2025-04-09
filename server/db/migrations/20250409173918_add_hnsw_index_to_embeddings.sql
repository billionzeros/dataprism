-- +goose NO TRANSACTION
--run this migration outside a transaction block.

-- +goose Up
-- Creates an HNSW index CONCURRENTLY for cosine distance search on the embedding column.
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vector_embeddings_embedding
ON vector_embeddings
USING hnsw (embedding vector_cosine_ops);

-- +goose Down
-- DROP INDEX CONCURRENTLY also cannot run inside a transaction.
DROP INDEX CONCURRENTLY IF EXISTS idx_vector_embeddings_embedding;