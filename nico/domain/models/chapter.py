"""Chapter model - organizational unit within a story."""
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, OrderableMixin, TimestampMixin

if TYPE_CHECKING:
    from .scene import Scene
    from .story import Story


class Chapter(Base, TimestampMixin, OrderableMixin):
    """A Chapter within a Story/Volume.
    
    Chapters are the primary organizational unit within a narrative work.
    They contain scenes (fiction) or sections (non-fiction). Chapters can
    be reordered via drag-and-drop.
    
    Attributes:
        id: Primary key
        story_id: Foreign key to parent story
        title: Chapter title
        description: Optional chapter synopsis or notes
        number: Chapter number (can differ from position for numbered chapters)
        word_count: Calculated word count from all scenes
        exclude_from_ai: If True, don't send this chapter's content to AI
        metadata: Flexible JSONB for chapter-specific settings
        position: Order within parent story
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        story: Parent story
        scenes: Collection of scenes/sections in this chapter
    """
    
    __tablename__ = "chapters"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    story_id: Mapped[int] = mapped_column(
        ForeignKey("stories.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Word count (aggregated from scenes)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # AI settings
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    story: Mapped["Story"] = relationship("Story", back_populates="chapters")
    scenes: Mapped[List["Scene"]] = relationship(
        "Scene",
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="Scene.position",
    )
    
    def __repr__(self) -> str:
        return f"<Chapter(id={self.id}, title='{self.title}')>"
