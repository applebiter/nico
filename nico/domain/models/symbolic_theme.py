"""SymbolicTheme model - high-level thematic dimension."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project
    from .symbolic_motif import SymbolicMotif


class SymbolicTheme(Base, TimestampMixin):
    """A high-level symbolic theme explored in the project.
    
    Represents a deeper thematic dimension the author wants to explore.
    Examples: "Control and Autonomy", "Identity and Performance", "Loss and Memory"
    
    Themes are intentionally private by default - they represent the author's
    deepest intentions and should not be exposed to AI unless explicitly enabled.
    
    Attributes:
        id: Primary key
        project_id: Foreign key to parent project
        title: Theme name (e.g., "Control and Autonomy")
        description: Private author notes on what this theme explores
        visibility: Privacy level (private/shared/ai_enabled)
        intensity_target: How heavy or subtle (subtle/moderate/prominent)
        exclude_from_ai: If True, never include in AI context
        metadata: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        project: Parent project
        motifs: Associated symbolic motifs
    """
    
    __tablename__ = "symbolic_themes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Core attributes
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Privacy and visibility
    visibility: Mapped[str] = mapped_column(
        String(50), 
        default="private",
        nullable=False,
    )  # private, shared, ai_enabled
    
    # Guidance
    intensity_target: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
    )  # subtle, moderate, prominent
    
    # AI settings
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Metadata
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="symbolic_themes")
    motifs: Mapped[list["SymbolicMotif"]] = relationship(
        "SymbolicMotif",
        back_populates="themes",
        secondary="symbolic_theme_motif_association",
    )
    
    def __repr__(self) -> str:
        return f"<SymbolicTheme(id={self.id}, title='{self.title}')>"
