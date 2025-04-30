# app/models/document.py

import uuid
import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import DateTime, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# Import the Base class
from app.db.base_class import Base

if TYPE_CHECKING:
    from .workspace import Workspace
    from .block import Block
    from .block_matrix import BlockMatrix

class Document(Base):
    """
    Represents a collection of blocks within a workspace.
    """
    __tablename__ = "documents"

    # Primary key for the document
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Foreign Key to Workspace
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Document metadata
    title: Mapped[str] = mapped_column(Text, nullable=True, default="") # Text allows longer titles

    # Foreign Key to the root Block (nullable)
    root_block_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("blocks.id", ondelete="SET NULL", use_alter=True, name="fk_document_root_block"),
        nullable=True,
        index=True
    )

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
    # Many-to-One relationship with Workspace
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="documents")

    # One-to-Many relationship with Block
    # Represents all blocks directly belonging to this document
    blocks: Mapped[List["Block"]] = relationship(
        "Block",
        back_populates="document",
        cascade="all, delete-orphan",
        foreign_keys="[Block.document_id]", # Specify foreign key if ambiguous
        lazy="selectin"
    )

    # One-to-One relationship with BlockMatrix
    # Represents the structural links between blocks in this document
    block_matrix: Mapped["BlockMatrix"] = relationship(
        "BlockMatrix",
        back_populates="document",
        cascade="all, delete-orphan",
        foreign_keys="[BlockMatrix.document_id]", # Specify foreign key
        lazy="selectin"
    )


    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', workspace_id='{self.workspace_id}')>"
