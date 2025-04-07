-- +goose Up
-- +goose StatementBegin
-- Enable UUID generation function if not already enabled (requires uuid-ossp extension)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- Or pgcrypto for gen_random_uuid()

-- Create documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    root_block_id UUID, -- Foreign key constraint added later
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE -- GORM soft delete column
);

-- Add indexes for documents table
CREATE INDEX idx_documents_root_block_id ON documents(root_block_id);
CREATE INDEX idx_documents_deleted_at ON documents(deleted_at);

-- Create blocks table
CREATE TABLE blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL, -- Foreign key constraint added later
    is_root BOOLEAN DEFAULT false,
    next_block_id UUID, -- Foreign key constraint added later
    prev_block_id UUID, -- Foreign key constraint added later
    parent_block_id UUID, -- Foreign key constraint added later
    parent_block_index INTEGER,
    type VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE -- GORM soft delete column
);

-- Add indexes for blocks table
CREATE INDEX idx_blocks_document_id ON blocks(document_id);
CREATE INDEX idx_blocks_next_block_id ON blocks(next_block_id);
CREATE INDEX idx_blocks_prev_block_id ON blocks(prev_block_id);
CREATE INDEX idx_blocks_parent_block_id ON blocks(parent_block_id);
CREATE INDEX idx_blocks_deleted_at ON blocks(deleted_at);

-- Add foreign key constraints
-- Note: We add these after both tables are created to avoid dependency issues.

-- Link documents.root_block_id to blocks.id
ALTER TABLE documents
ADD CONSTRAINT fk_documents_root_block
FOREIGN KEY (root_block_id) REFERENCES blocks(id) ON DELETE SET NULL; -- Set root to NULL if the block is deleted

-- Link blocks.document_id to documents.id
ALTER TABLE blocks
ADD CONSTRAINT fk_blocks_document
FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE; -- Delete blocks if the document is deleted

-- Link blocks.next_block_id to blocks.id (self-referencing)
ALTER TABLE blocks
ADD CONSTRAINT fk_blocks_next_block
FOREIGN KEY (next_block_id) REFERENCES blocks(id) ON DELETE SET NULL; -- Set next to NULL if the referenced block is deleted

-- Link blocks.prev_block_id to blocks.id (self-referencing)
ALTER TABLE blocks
ADD CONSTRAINT fk_blocks_prev_block
FOREIGN KEY (prev_block_id) REFERENCES blocks(id) ON DELETE SET NULL; -- Set prev to NULL if the referenced block is deleted

-- Link blocks.parent_block_id to blocks.id (self-referencing)
ALTER TABLE blocks
ADD CONSTRAINT fk_blocks_parent_block
FOREIGN KEY (parent_block_id) REFERENCES blocks(id) ON DELETE SET NULL; -- Set parent to NULL if the referenced block is deleted
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin

-- Drop foreign key constraints first to avoid dependency errors
ALTER TABLE documents DROP CONSTRAINT IF EXISTS fk_documents_root_block;
ALTER TABLE blocks DROP CONSTRAINT IF EXISTS fk_blocks_document;
ALTER TABLE blocks DROP CONSTRAINT IF EXISTS fk_blocks_next_block;
ALTER TABLE blocks DROP CONSTRAINT IF EXISTS fk_blocks_prev_block;
ALTER TABLE blocks DROP CONSTRAINT IF EXISTS fk_blocks_parent_block;

-- Drop indexes (optional, as they are often dropped with the table, but explicit is fine)
DROP INDEX IF EXISTS idx_documents_root_block_id;
DROP INDEX IF EXISTS idx_documents_deleted_at;
DROP INDEX IF EXISTS idx_blocks_document_id;
DROP INDEX IF EXISTS idx_blocks_next_block_id;
DROP INDEX IF EXISTS idx_blocks_prev_block_id;
DROP INDEX IF EXISTS idx_blocks_parent_block_id;
DROP INDEX IF EXISTS idx_blocks_deleted_at;

-- Drop the tables (reverse order of creation)
DROP TABLE IF EXISTS blocks;
DROP TABLE IF EXISTS documents;

-- +goose StatementEnd