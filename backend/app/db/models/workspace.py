# app/models/workspace.py

import uuid
import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# Import the Base class
from app.db.base_class import Base

if TYPE_CHECKING:
    from .document import Document
    from .workspace_upload import WorkspaceUpload

class Workspace(Base):
    """
    Represents a higher-level collection of documents and related uploads.
    """
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    # Soft Delete
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    # --- Relationships ---
    # One-to-Many relationship with Document
    # `back_populates` links this relationship to the one defined in the Document model
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="workspace", cascade="all, delete-orphan"
    )

    # One-to-Many relationship with the association table WorkspaceUpload
    workspace_uploads: Mapped[List["WorkspaceUpload"]] = relationship(
        "WorkspaceUpload", back_populates="workspace", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Workspace(id={self.id}, name='{self.name}')>"

