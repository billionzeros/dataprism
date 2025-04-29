# app/models/upload.py

import uuid
import enum
import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import DateTime, func, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import ENUM as PG_Enum

# Import the Base class
from app.db.base_class import Base

if TYPE_CHECKING:
    from .workspace_upload import WorkspaceUpload

# 1. Define Enum for UploadType
class UploadType(str, enum.Enum):
    DOCUMENT = "document"
    BLOCK = "block"
    CSV = "csv"
    PDF = "pdf"
    # Add other types as needed

# 2. Define the Upload Model
class Upload(Base):
    """
    Stores information about files uploaded by users or associated with other entities.
    """
    __tablename__ = "uploads"

    # Optional: Add indexes
    __table_args__ = (
        Index('ix_upload_source', 'source_type', 'source_identifier'),
    )

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

    # Source Information
    source_type: Mapped[UploadType] = mapped_column(
        PG_Enum(UploadType, name="upload_type_enum", create_type=False), # Store as VARCHAR
        nullable=False, index=True
    )
    source_identifier: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    file_location: Mapped[str] = mapped_column(Text, nullable=False) # Path or URL

    # --- Relationships ---
    # One-to-Many relationship with the association table WorkspaceUpload
    workspace_links: Mapped[List[WorkspaceUpload]] = relationship(
        "WorkspaceUpload", back_populates="upload", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Upload(id={self.id}, type='{self.source_type}', location='{self.file_location[:30]}...')>"

