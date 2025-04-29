# app/models/workspace_upload.py

import uuid
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, func, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.db.base_class import Base

if TYPE_CHECKING:
    from .workspace import Workspace
    from .upload import Upload 

class WorkspaceUpload(Base):
    """
    Association table linking Workspaces and Uploads (Many-to-Many).
    """
    __tablename__ = "workspace_uploads"

    # Composite Primary Key (as defined in GORM)
    # SQLAlchemy requires defining this explicitly if no single 'id' column exists
    __table_args__ = (
        PrimaryKeyConstraint('workspace_id', 'upload_id', name='pk_workspace_upload'),
    )

    # Foreign Key to Workspace
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        # primary_key=True # Part of composite PK defined in __table_args__
    )

    # Foreign Key to Upload
    upload_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("uploads.id", ondelete="CASCADE"),
        # primary_key=True # Part of composite PK defined in __table_args__
    )

    # Timestamp for the association
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # --- Relationships ---
    # Many-to-One relationship back to Workspace
    workspace: Mapped[Workspace] = relationship("Workspace", back_populates="workspace_uploads")

    # Many-to-One relationship back to Upload
    upload: Mapped[Upload] = relationship("Upload", back_populates="workspace_links")


    def __repr__(self):
        return f"<WorkspaceUpload(workspace_id={self.workspace_id}, upload_id='{self.upload_id}')>"

