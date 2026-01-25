"""SymbolicMotif model - recurring element that contributes to themes."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, Table, Text, Column, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project
    from .symbolic_theme import SymbolicTheme
    from .symbolic_occurrence import SymbolicOccurrence
    from .character_motif_relationship import CharacterMotifRelationship


# Association table for many-to-many between themes and motifs
symbolic_theme_motif_association = Table(
    "symbolic_theme_motif_association",
    Base.metadata,
    Column("theme_id", Integer, ForeignKey("symbolic_themes.id", ondelete="CASCADE")),
    Column("motif_id", Integer, ForeignKey("symbolic_motifs.id", ondelete="CASCADE")),
)


class SymbolicMotif(Base, TimestampMixin):
    """A specific recurring element that contributes to symbolic themes.
    
    Motifs are the building blocks of symbolic meaning - specific patterns
    that recur throughout the narrative. Examples: "Locked doors and boundaries",
    "Surveillance language", "Permission dynamics"
    
    Motifs track *what* appears, while SymbolicOccurrence tracks *where* and *how strongly*.
    
    Attributes:
        id: Primary key
        project_id: Foreign key to parent project
        name: Motif name (e.g., "Confinement Imagery")
        motif_type: Category of motif
        description: What this motif encompasses
        intended_arc: How this motif should evolve over the story
        exclude_from_ai: If True, don't include in AI context
        metadata: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        project: Parent project
        themes: Associated symbolic themes (many-to-many)
        occurrences: Scene-level tracking of where this motif appears
        character_relationships: Characters connected to this motif
    """
    
    __tablename__ = "symbolic_motifs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Core attributes
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    
    motif_type: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True,
    )  # imagery, dialogue_pattern, action_pattern, setting_element, power_dynamic
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Evolution guidance
    intended_arc: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
    )  # constant, escalating, diminishing, cycling
    
    # AI settings
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Metadata
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="symbolic_motifs")
    themes: Mapped[list["SymbolicTheme"]] = relationship(
        "SymbolicTheme",
        back_populates="motifs",
        secondary="symbolic_theme_motif_association",
    )
    occurrences: Mapped[list["SymbolicOccurrence"]] = relationship(
        "SymbolicOccurrence",
        back_populates="motif",
        cascade="all, delete-orphan",
    )
    character_relationships: Mapped[list["CharacterMotifRelationship"]] = relationship(
        "CharacterMotifRelationship",
        back_populates="motif",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<SymbolicMotif(id={self.id}, name='{self.name}')>"
