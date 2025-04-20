-- +goose Up
-- +goose StatementBegin

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create workspaces table
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);
CREATE INDEX idx_workspaces_deleted_at ON workspaces(deleted_at);
CREATE TRIGGER set_workspaces_timestamp
BEFORE UPDATE ON workspaces
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Create documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL, -- Foreign key added below
    title TEXT,
    root_block_id UUID, -- Foreign key added below
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);
CREATE INDEX idx_documents_workspace_id ON documents(workspace_id);
CREATE INDEX idx_documents_deleted_at ON documents(deleted_at);
CREATE INDEX idx_documents_root_block_id ON documents(root_block_id);
CREATE TRIGGER set_documents_timestamp
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Create blocks table
CREATE TABLE blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL, -- Foreign key added below
    document_id UUID NOT NULL, -- Foreign key added below
    type VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);
CREATE INDEX idx_blocks_workspace_id ON blocks(workspace_id);
CREATE INDEX idx_blocks_document_id ON blocks(document_id);
CREATE INDEX idx_blocks_deleted_at ON blocks(deleted_at);

-- Create block_matrix table (handles relationships)
CREATE TABLE block_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL, -- Foreign key added below
    document_id UUID NOT NULL, -- Foreign key added below
    block_id UUID NOT NULL, -- Foreign key added below
    is_root BOOLEAN NOT NULL DEFAULT false,
    next_block_id UUID, -- Foreign key added below
    prev_block_id UUID, -- Foreign key added below
    parent_block_id UUID, -- Foreign key added below
    level INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_block_matrix_doc_block UNIQUE (document_id, block_id)
);
CREATE INDEX idx_block_matrix_workspace_id ON block_matrix(workspace_id);
CREATE INDEX idx_block_matrix_document_id ON block_matrix(document_id);
CREATE INDEX idx_block_matrix_block_id ON block_matrix(block_id);
CREATE INDEX idx_block_matrix_next_block_id ON block_matrix(next_block_id);
CREATE INDEX idx_block_matrix_prev_block_id ON block_matrix(prev_block_id);
CREATE INDEX idx_block_matrix_parent_block_id ON block_matrix(parent_block_id);
CREATE INDEX idx_block_matrix_document_id_is_root ON block_matrix(document_id, is_root);


-- Create uploads table
CREATE TABLE uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL, -- Foreign key added below
    source_type TEXT NOT NULL,
    source_identifier TEXT NOT NULL,
    file_location TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);
CREATE INDEX idx_uploads_workspace_id ON uploads(workspace_id); -- Added index for FK
CREATE INDEX idx_uploads_deleted_at ON uploads(deleted_at);
CREATE INDEX idx_uploads_source_type ON uploads(source_type);
CREATE INDEX idx_uploads_source_identifier ON uploads(source_identifier);

-- Create Workspace Uploads table
CREATE TABLE workspace_uploads (
    workspace_id UUID NOT NULL,
    upload_id UUID NOT NULL,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Add if needed

    PRIMARY KEY (workspace_id, upload_id),

    CONSTRAINT fk_workspace_uploads_workspace
        FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_workspace_uploads_upload
        FOREIGN KEY (upload_id) REFERENCES uploads(id)
        ON DELETE CASCADE
);
CREATE INDEX idx_workspace_uploads_workspace_id ON workspace_uploads(workspace_id);
CREATE INDEX idx_workspace_uploads_upload_id ON workspace_uploads(upload_id);

-- Add Foreign Key Constraints AFTER all tables are created

-- Workspace FKs
ALTER TABLE documents ADD CONSTRAINT fk_documents_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE;
ALTER TABLE blocks ADD CONSTRAINT fk_blocks_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE;
ALTER TABLE block_matrix ADD CONSTRAINT fk_block_matrix_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE;
ALTER TABLE uploads ADD CONSTRAINT fk_uploads_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE;

-- Document FKs
ALTER TABLE blocks ADD CONSTRAINT fk_blocks_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE;
ALTER TABLE block_matrix ADD CONSTRAINT fk_block_matrix_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE;

-- Block FKs (linking within blocks/matrix)
ALTER TABLE documents ADD CONSTRAINT fk_documents_root_block FOREIGN KEY (root_block_id) REFERENCES blocks(id) ON DELETE SET NULL;
ALTER TABLE block_matrix ADD CONSTRAINT fk_block_matrix_block FOREIGN KEY (block_id) REFERENCES blocks(id) ON DELETE CASCADE;
ALTER TABLE block_matrix ADD CONSTRAINT fk_block_matrix_next_block FOREIGN KEY (next_block_id) REFERENCES blocks(id) ON DELETE SET NULL;
ALTER TABLE block_matrix ADD CONSTRAINT fk_block_matrix_prev_block FOREIGN KEY (prev_block_id) REFERENCES blocks(id) ON DELETE SET NULL;
ALTER TABLE block_matrix ADD CONSTRAINT fk_block_matrix_parent_block FOREIGN KEY (parent_block_id) REFERENCES blocks(id) ON DELETE SET NULL;

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin

-- Drop constraints first (in reverse order of addition or dependency)
ALTER TABLE block_matrix DROP CONSTRAINT IF EXISTS fk_block_matrix_parent_block;
ALTER TABLE block_matrix DROP CONSTRAINT IF EXISTS fk_block_matrix_prev_block;
ALTER TABLE block_matrix DROP CONSTRAINT IF EXISTS fk_block_matrix_next_block;
ALTER TABLE block_matrix DROP CONSTRAINT IF EXISTS fk_block_matrix_block;
ALTER TABLE documents DROP CONSTRAINT IF EXISTS fk_documents_root_block;

ALTER TABLE block_matrix DROP CONSTRAINT IF EXISTS fk_block_matrix_document;
ALTER TABLE blocks DROP CONSTRAINT IF EXISTS fk_blocks_document;

ALTER TABLE uploads DROP CONSTRAINT IF EXISTS fk_uploads_workspace;
ALTER TABLE block_matrix DROP CONSTRAINT IF EXISTS fk_block_matrix_workspace;
ALTER TABLE blocks DROP CONSTRAINT IF EXISTS fk_blocks_workspace;
ALTER TABLE documents DROP CONSTRAINT IF EXISTS fk_documents_workspace;

-- Drop triggers
DROP TRIGGER IF EXISTS set_uploads_timestamp ON uploads;
DROP TRIGGER IF EXISTS set_block_matrix_timestamp ON block_matrix;
DROP TRIGGER IF EXISTS set_blocks_timestamp ON blocks;
DROP TRIGGER IF EXISTS set_documents_timestamp ON documents;
DROP TRIGGER IF EXISTS set_workspaces_timestamp ON workspaces;

-- Drop tables in reverse order of creation (and dependency)
DROP TABLE IF EXISTS workspace_uploads;
DROP TABLE IF EXISTS uploads;
DROP TABLE IF EXISTS block_matrix;
DROP TABLE IF EXISTS blocks;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS workspaces;

-- Drop the trigger function
DROP FUNCTION IF EXISTS trigger_set_timestamp();

-- +goose StatementEnd