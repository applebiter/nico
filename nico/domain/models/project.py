"""Project model - top-level container for a narrative universe."""
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .story import Story
    from .symbolic_theme import SymbolicTheme
    from .symbolic_motif import SymbolicMotif
    from .media import Media


class Project(Base, TimestampMixin):
    """A Project represents a narrative universe or literary collection.
    
    A project can contain multiple stories (for series) or volumes (for non-fiction).
    It serves as the top-level organizational unit and is typically stored as a
    folder on disk containing the database and media files.
    
    Attributes:
        id: Primary key
        title: Project name
        description: Optional overview of the project
        author: Project author name
        metadata: Flexible JSONB field for user-defined project settings
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        stories: Collection of stories/volumes in this project
    """
    
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Flexible metadata for user preferences, AI settings, etc.
    # Example: {"local_only_ai": true, "default_font": "Arial", "target_word_count": 80000}
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    stories: Mapped[List["Story"]] = relationship(
        "Story",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Story.position",
    )
    symbolic_themes: Mapped[List["SymbolicTheme"]] = relationship(
        "SymbolicTheme",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    symbolic_motifs: Mapped[List["SymbolicMotif"]] = relationship(
        "SymbolicMotif",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    media: Mapped[List["Media"]] = relationship(
        "Media",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, title='{self.title}')>"
