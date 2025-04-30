# app/models/block.py

import uuid
import enum
import datetime
from typing import Dict, Any, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, func, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import JSONB 

from app.db.base_class import Base

if TYPE_CHECKING:
    from .document import Document
    from .workspace import Workspace
    from .block_matrix import BlockMatrix

class BlockType(str, enum.Enum):
    """
    Enumeration for different types of content blocks.
    Inheriting from 'str' makes it easily serializable.
    """
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    QUOTE = "quote"
    CODE = "code"
    EMBED = "embed"
    IMAGE = "image"
    TABLE = "table"
    LINE_CHART = "line-chart"
    BAR_CHART = "bar-chart"
    PIE_CHART = "pie-chart"

class Block(Base):
    """
    Represents a content block within a document and workspace.
    """
    __tablename__ = "blocks"

    # Primary key for the block
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Foreign Key to Workspace
    # Adjust 'workspaces.id' if your workspace table/column names differ
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"), # Replicates constraint:OnDelete:CASCADE
        nullable=False,
        index=True
    )

    # Foreign Key to Document
    # Adjust 'documents.id' if your document table/column names differ
    document_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    type: Mapped[BlockType] = mapped_column(
        SQLAlchemyEnum(BlockType, name="blocktype_enum", native_enum=False),
        nullable=False
    )

    content: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # updated_at is often useful as well
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    # --- Relationships ---
    # One-to-One relationship with Document
    document: Mapped["Document"] = relationship("Document", back_populates="blocks", foreign_keys=[document_id])

    # Many-to-One relationship with Workspace
    workspace: Mapped["Workspace"] = relationship("Workspace", foreign_keys=[workspace_id])
    
    # One-to-One relationship with BlockMatrix (if applicable)
    block_matrix: Mapped["BlockMatrix"] = relationship("BlockMatrix", back_populates="block", foreign_keys="[BlockMatrix.block_id]", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Block(id={self.id}, type='{self.type}', doc_id='{self.document_id}')>"
