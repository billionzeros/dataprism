-- +goose Up
-- +goose StatementBegin
SELECT 'up SQL query';

-- Create documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    root_block_id UUID, -- Foreign key added later after blocks table exists
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);
CREATE INDEX idx_documents_deleted_at ON documents(deleted_at);
CREATE INDEX idx_documents_root_block_id ON documents(root_block_id);


-- Create blocks table
CREATE TABLE blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    type VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,

    CONSTRAINT fk_blocks_document
        FOREIGN KEY (document_id) REFERENCES documents(id)
        ON DELETE CASCADE
);
CREATE INDEX idx_blocks_document_id ON blocks(document_id);
CREATE INDEX idx_blocks_deleted_at ON blocks(deleted_at);


-- Create block_matrix table (handles relationships)
CREATE TABLE block_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    block_id UUID NOT NULL, -- Refers to the actual block in the blocks table
    is_root BOOLEAN NOT NULL DEFAULT false,
    next_block_id UUID, -- Refers to the block_id of the next block in sequence
    prev_block_id UUID, -- Refers to the block_id of the previous block in sequence
    parent_block_id UUID, -- Refers to the block_id of the parent block (for nesting)
    level INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_block_matrix_document
        FOREIGN KEY (document_id) REFERENCES documents(id)
        ON DELETE CASCADE, -- If document is deleted, delete its matrix entries
    CONSTRAINT fk_block_matrix_block
        FOREIGN KEY (block_id) REFERENCES blocks(id)
        ON DELETE CASCADE, -- If a block is deleted, delete its matrix entry
    CONSTRAINT fk_block_matrix_next_block
        FOREIGN KEY (next_block_id) REFERENCES blocks(id)
        ON DELETE SET NULL, -- If the next block is deleted, just nullify the link
    CONSTRAINT fk_block_matrix_prev_block
        FOREIGN KEY (prev_block_id) REFERENCES blocks(id)
        ON DELETE SET NULL, -- If the previous block is deleted, just nullify the link
    CONSTRAINT fk_block_matrix_parent_block
        FOREIGN KEY (parent_block_id) REFERENCES blocks(id)
        ON DELETE SET NULL, -- If the parent block is deleted, just nullify the link

    -- Unique constraint: A block should only appear once in a document's matrix
    CONSTRAINT uq_block_matrix_doc_block UNIQUE (document_id, block_id)
);

-- Indexes for block_matrix
CREATE INDEX idx_block_matrix_document_id ON block_matrix(document_id);
CREATE INDEX idx_block_matrix_block_id ON block_matrix(block_id);
CREATE INDEX idx_block_matrix_next_block_id ON block_matrix(next_block_id);
CREATE INDEX idx_block_matrix_prev_block_id ON block_matrix(prev_block_id);
CREATE INDEX idx_block_matrix_parent_block_id ON block_matrix(parent_block_id);
CREATE INDEX idx_block_matrix_document_id_is_root ON block_matrix(document_id, is_root); -- For finding the root efficiently


-- Add the foreign key constraint for documents.root_block_id now that blocks table exists
ALTER TABLE documents
ADD CONSTRAINT fk_documents_root_block
    FOREIGN KEY (root_block_id) REFERENCES blocks(id)
    ON DELETE SET NULL; -- If the root block is deleted, set root_block_id to NULL


-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
SELECT 'down SQL query';

-- Drop constraints first if needed (like the one added via ALTER TABLE)
ALTER TABLE documents DROP CONSTRAINT IF EXISTS fk_documents_root_block;

-- Drop tables in reverse order of creation
DROP TABLE IF EXISTS block_matrix;
DROP TABLE IF EXISTS blocks;
DROP TABLE IF EXISTS documents;

-- +goose StatementEnd