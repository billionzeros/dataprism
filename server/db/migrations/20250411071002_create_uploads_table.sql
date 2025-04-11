-- +goose Up
-- +goose StatementBegin
SELECT 'up SQL query for creating uploads table and related types';
-- +goose StatementEnd

-- Create the uploads table
CREATE TABLE uploads (
    -- Unique identifier for the upload
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Created At timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Updated At timestamp
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Deleted At timestamp for soft deletes
    deleted_at TIMESTAMPTZ, -- Nullable for soft deletes

    -- Different types of uploads
    source_type TEXT NOT NULL,

    -- Source identifier for the upload, e.g., user ID, system ID, File ID, etc.
    source_identifier TEXT NOT NULL,

    -- Location of the file in the storage system
    file_location TEXT NOT NULL
);

-- Create indexes for faster querying
-- Index for soft deletes (querying non-deleted records)
CREATE INDEX idx_uploads_deleted_at ON uploads(deleted_at);

-- Index for filtering by source type
CREATE INDEX idx_uploads_source_type ON uploads(source_type);

-- Index for filtering by source identifier
CREATE INDEX idx_uploads_source_identifier ON uploads(source_identifier);


-- +goose Down
-- +goose StatementBegin
SELECT 'down SQL query for dropping uploads table and related types';
-- +goose StatementEnd

-- Drop the table first (depends on the type)
DROP TABLE IF EXISTS uploads;

-- Drop the custom enum type
DROP TYPE IF EXISTS upload_type;