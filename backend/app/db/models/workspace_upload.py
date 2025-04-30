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

    __table_args__ = (
        PrimaryKeyConstraint('workspace_id', 'upload_id', name='pk_workspace_upload'),
    )

    # Primary key for the association entry itself
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), default=uuid.uuid4
    )

    # Foreign Key to Workspace
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
    )

    # Foreign Key to Upload
    upload_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("uploads.id", ondelete="CASCADE"),
    )

    # Timestamp for the association
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # --- Relationships ---
    # Many-to-One back to Workspace
    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        overlaps="uploads,workspaces"
    )

    # Many-to-One back to Upload
    upload: Mapped["Upload"] = relationship(
        "Upload",
        overlaps="uploads,workspaces"
    )


    def __repr__(self):
        return f"<WorkspaceUpload(workspace_id={self.workspace_id}, upload_id='{self.upload_id}')>"

