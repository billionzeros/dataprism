# app/models/vector_embedding.py

import uuid
import enum
import datetime
from typing import Optional, List

from sqlalchemy import DateTime, func, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import ENUM as PG_Enum

# Import the Base class
from app.db.base_class import Base
from pgvector.sqlalchemy import Vector

class EmbeddingSourceType(str, enum.Enum):
    DOCUMENT = "document"
    BLOCK = "block"
    CSV_COLUMN = "csv"
    POSTGRES_COLUMN = "postgres"
    PDF_CHUNK = "pdf_chunk"
    USER_PROFILE = "user_profile"
    USER_MEMORY = "user_memory"
    UNKNOWN = "unknown"

class VectorEmbedding(Base):
    """
    Stores vector embeddings generated from various sources.
    Requires the 'vector' extension enabled in PostgreSQL and the
    'sqlalchemy-pgvector' library installed.
    """
    __tablename__ = "vector_embeddings"

    __table_args__ = (
        Index('ix_vector_embedding_source', 'source_type', 'source_identifier'),
    )

    # Primary key for the vector embedding
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Soft Delete
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    source_type: Mapped[EmbeddingSourceType] = mapped_column(
        PG_Enum(EmbeddingSourceType, name="embedding_source_type_enum", create_type=False), # create_type=False stores as VARCHAR
        nullable=False, index=True
    )

    source_identifier: Mapped[str] = mapped_column(Text, nullable=False, index=True) # Use Text for flexibility
    related_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    column_or_chunk_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    original_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Store original text if possible

    embedding: Mapped[List[float]] = mapped_column(Vector(768), nullable=False)

    def __repr__(self):
        return f"<VectorEmbedding(id={self.id}, source_type='{self.source_type}', source_id='{self.source_identifier}')>"
