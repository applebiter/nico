"""Story model - individual narrative work within a project."""
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, OrderableMixin, TimestampMixin

if TYPE_CHECKING:
    from .chapter import Chapter
    from .project import Project


class Story(Base, TimestampMixin, OrderableMixin):
    """A Story (fiction) or Volume (non-fiction) within a Project.
    
    Represents a single narrative work - could be a novel, screenplay, 
    non-fiction book, or other complete work. Stories can be reordered
    within a project for series management.
    
    Attributes:
        id: Primary key
        project_id: Foreign key to parent project
        title: Story/volume title
        subtitle: Optional subtitle
        description: Synopsis or overview
        is_fiction: True for stories, False for volumes (affects UI terminology)
        word_count_target: Optional target word count
        word_count_actual: Current word count (calculated from scenes)
        metadata: Flexible JSONB for user settings, templates, etc.
        exclude_from_ai: If True, don't send this story's content to AI
        position: Order within parent project
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        project: Parent project
        chapters: Collection of chapters in this story
    """
    
    __tablename__ = "stories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    subtitle: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Fiction vs non-fiction affects UI terminology (scene vs section)
    is_fiction: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Word count tracking
    word_count_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    word_count_actual: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # AI and template settings
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="stories")
    chapters: Mapped[List["Chapter"]] = relationship(
        "Chapter",
        back_populates="story",
        cascade="all, delete-orphan",
        order_by="Chapter.position",
    )
    
    def __repr__(self) -> str:
        return f"<Story(id={self.id}, title='{self.title}')>"
