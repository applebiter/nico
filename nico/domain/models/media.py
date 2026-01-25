"""Media model - reusable media library items (images, audio, video)."""
from typing import TYPE_CHECKING, Optional
from datetime import datetime
from pathlib import Path

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project
    from .media_attachment import MediaAttachment


class Media(Base, TimestampMixin):
    """A media library item (image, audio, or video).
    
    Media items are stored in the project's media/ folder and can be
    attached to any entity (characters, scenes, chapters, etc.).
    
    Following the architecture's media storage pattern:
    - media/{media_id}/original.ext
    - media/{media_id}/thumb.webp (for images)
    - media/{media_id}/preview.mp3 (for audio, optional)
    - media/{media_id}/waveform.json (for audio, optional)
    
    Attributes:
        id: Primary key
        project_id: Foreign key to parent project
        media_type: Type of media (image/audio/video)
        original_filename: Original filename when uploaded
        file_path: Relative path to original file (from project root)
        thumbnail_path: Relative path to thumbnail (if applicable)
        mime_type: MIME type (image/jpeg, audio/mpeg, etc.)
        file_size: Size in bytes
        width: Image/video width in pixels (if applicable)
        height: Image/video height in pixels (if applicable)
        duration: Audio/video duration in seconds (if applicable)
        title: Optional user-provided title
        description: Optional description
        tags: Optional tags for organization
        source_url: Optional URL if sourced from web
        attribution: Optional attribution/credit text
        file_hash: SHA256 hash for deduplication
        exclude_from_ai: If True, don't send to AI services
        metadata: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        project: Parent project
        attachments: All attachments of this media to entities
    """
    
    __tablename__ = "media"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Media type and files
    media_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
    )  # image, audio, video
    
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA256
    
    # Dimensions (for images/videos)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Duration (for audio/video)
    duration: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # User metadata
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Source information
    source_url: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    attribution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # AI settings
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Metadata
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Semantic search embedding (visual for images, text for title+description)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(768), nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="media")
    attachments: Mapped[list["MediaAttachment"]] = relationship(
        "MediaAttachment",
        back_populates="media",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Media(id={self.id}, type='{self.media_type}', filename='{self.original_filename}')>"
    
    def get_display_title(self) -> str:
        """Get display title (user title or filename)."""
        return self.title or self.original_filename
