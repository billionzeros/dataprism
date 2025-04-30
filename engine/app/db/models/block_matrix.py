# app/models/block_matrix.py

import uuid
import datetime
from typing import Optional,  TYPE_CHECKING

from sqlalchemy import (
    DateTime, func, ForeignKey, Boolean, Integer,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# Import the Base class
from app.db.base_class import Base

if TYPE_CHECKING:
    from .workspace import Workspace
    from .document import Document
    from .block import Block

class BlockMatrix(Base):
    """
    Represents the structural relationship (matrix) between blocks within a document.
    Handles linking (next, previous, parent) and hierarchy (level, root).
    """
    __tablename__ = "block_matrix"

    # Define constraints (like unique index in GORM)
    __table_args__ = (
        UniqueConstraint('document_id', 'block_id', name='uq_doc_block'),
        # Add other constraints or indexes if needed
        # Index('ix_blockmatrix_parent', 'parent_block_id'),
    )

    # Primary key for the matrix entry itself
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

    # Foreign Key to Document
    document_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True # Also part of the UniqueConstraint above
    )

    # Foreign Key to the actual Block this matrix entry represents
    block_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("blocks.id", ondelete="CASCADE"),
        nullable=False,
        index=True # Also part of the UniqueConstraint above
    )

    # Structure fields
    is_root: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Self-referential Foreign Keys for linking blocks (nullable)
    # Use use_alter=True for potentially circular foreign keys
    next_block_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("blocks.id", ondelete="SET NULL", use_alter=True, name="fk_blockmatrix_next"),
        nullable=True, index=True
    )
    prev_block_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("blocks.id", ondelete="SET NULL", use_alter=True, name="fk_blockmatrix_prev"),
        nullable=True, index=True
    )
    parent_block_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("blocks.id", ondelete="SET NULL", use_alter=True, name="fk_blockmatrix_parent"),
        nullable=True, index=True
    )

    # Timestamp
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # --- Relationships ---
    # Many-to-One relationship back to the Workspace
    workspace: Mapped["Workspace"] = relationship("Workspace", foreign_keys=[workspace_id])

    # Many-to-One relationship back to the Document
    document: Mapped["Document"] = relationship("Document", back_populates="block_matrix", foreign_keys=[document_id])

    # Many-to-One relationship back to the specific Block this entry represents
    block: Mapped["Block"] = relationship("Block", back_populates="block_matrix", foreign_keys=[block_id])

    def __repr__(self):
        return f"<BlockMatrix(doc_id={self.document_id}, block_id='{self.block_id}', level={self.level})>"

    # --- Hooks ---
    # GORM Hooks (BeforeCreate, AfterDelete) logic needs to be implemented
    # outside the model, typically in the service/repository layer using
    # SQLAlchemy session events or explicit calls before/after session operations.
