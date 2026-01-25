"""Scene model - the actual writing surface containing content."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from .base import Base, OrderableMixin, TimestampMixin

if TYPE_CHECKING:
    from .chapter import Chapter
    from .symbolic_occurrence import SymbolicOccurrence


class Scene(Base, TimestampMixin, OrderableMixin):
    """A Scene (fiction) or Section (non-fiction) within a Chapter.
    
    This is where the actual writing happens. Scenes contain the raw content
    and support rich text editing with annotations, comments, and highlights.
    The content is stored as HTML/structured format compatible with the
    ProseMirror/TipTap editor.
    
    Attributes:
        id: Primary key
        chapter_id: Foreign key to parent chapter
        title: Scene/section title
        content: Rich text content (HTML/JSON from ProseMirror)
        summary: Optional brief summary of the scene
        word_count: Calculated word count from content
        beat: Optional story beat or structural note (e.g., "inciting incident")
        exclude_from_ai: If True, don't send this scene's content to AI
        metadata: Flexible JSONB for scene-specific settings, tags, etc.
        position: Order within parent chapter
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        chapter: Parent chapter
    """
    
    __tablename__ = "scenes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Main content - stored as HTML or ProseMirror JSON
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Word count (calculated from content)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Story structure metadata
    beat: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # AI settings
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Flexible metadata: POV character, setting, tags, etc.
    # Example: {"pov": "Alice", "setting": "London", "tags": ["action", "romance"]}
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Semantic search embedding (generated from content + summary + beat + meta)
    scene_embedding: Mapped[Optional[list]] = mapped_column(Vector(768), nullable=True)
    
    # Relationships
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="scenes")
    symbolic_occurrences: Mapped[list["SymbolicOccurrence"]] = relationship(
        "SymbolicOccurrence",
        back_populates="scene",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Scene(id={self.id}, title='{self.title}', words={self.word_count})>"
