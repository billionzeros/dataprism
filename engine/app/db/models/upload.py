# app/models/upload.py

import uuid
import enum
import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import ENUM as PG_Enum

# Import the Base class
from app.db.base_class import Base

if TYPE_CHECKING:
    from .workspace import Workspace

class UploadType(str, enum.Enum):
    CSV = "csv"
    PDF = "pdf"
    PARQUET = "parquet"

# 2. Define the Upload Model
class Upload(Base):
    """
    Stores information about files uploaded by users or associated with other entities.
    """
    __tablename__ = "uploads"

    # Primary key for the upload
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Source Information
    file_name: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[UploadType] = mapped_column(
        PG_Enum(UploadType, name="upload_type_enum", create_type=False), # Store as VARCHAR
        nullable=False, index=True
    )
    file_size: Mapped[int] = mapped_column(nullable=False) # Size in bytes
    storage_key: Mapped[str] = mapped_column(Text, nullable=False) # R2 Unique key for the file
    storage_url: Mapped[str] = mapped_column(Text, nullable=False) # Path or URL, e.g., S3 URL

    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Soft Delete
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    # --- Relationships ---
    # Many-to-Many relationship with Workspace via WorkspaceUpload
    workspaces: Mapped[List["Workspace"]] = relationship(
        "Workspace",
        secondary="workspace_uploads",
        back_populates="uploads",
    )

    def __repr__(self):
        return f"<Upload(id={self.id}, type='{self.file_type}', name='{self.file_name}')>"

