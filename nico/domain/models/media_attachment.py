"""MediaAttachment model - links media to any entity."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, OrderableMixin

if TYPE_CHECKING:
    from .media import Media


class MediaAttachment(Base, TimestampMixin, OrderableMixin):
    """Links a media item to an entity (polymorphic).
    
    This allows any entity (character, scene, chapter, story, location, event)
    to have attached media items. Media can be attached to multiple entities.
    
    Uses polymorphic association pattern:
    - entity_type: The type of entity (character, scene, chapter, etc.)
    - entity_id: The ID of the entity
    
    Attributes:
        id: Primary key
        media_id: Foreign key to media item
        entity_type: Type of entity this is attached to
        entity_id: ID of the entity
        caption: Optional caption for this attachment
        position: Order within entity's media list
        metadata: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        media: The media item being attached
    """
    
    __tablename__ = "media_attachments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    media_id: Mapped[int] = mapped_column(
        ForeignKey("media.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Polymorphic association
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # character, scene, chapter, story, location, event
    
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Attachment metadata
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    media: Mapped["Media"] = relationship("Media", back_populates="attachments")
    
    def __repr__(self) -> str:
        return f"<MediaAttachment(id={self.id}, media={self.media_id}, {self.entity_type}={self.entity_id})>"
