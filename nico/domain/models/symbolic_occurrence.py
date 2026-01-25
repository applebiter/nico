"""SymbolicOccurrence model - tracks when/how motifs appear in scenes."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .scene import Scene
    from .symbolic_motif import SymbolicMotif


class SymbolicOccurrence(Base, TimestampMixin):
    """Tracks when and how a symbolic motif appears in the narrative.
    
    Occurrences are scene-level tracking of symbolic motifs. They record
    intensity, author notes, and whether the occurrence is a contrast or
    too explicit.
    
    This enables "accumulation over assignment" - patterns emerge through
    tracking recurrence, density, and rhythm rather than rigid one-to-one
    correspondences.
    
    Attributes:
        id: Primary key
        scene_id: Which scene this occurs in
        motif_id: Which motif appears
        intensity: How prominent (0-10 scale)
        note: Author's private note about this occurrence
        is_contrast: Does this scene deliberately subvert the motif?
        is_explicit: Is the symbolic layer too obvious here?
        metadata: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        scene: The scene where this occurs
        motif: The motif that appears
    """
    
    __tablename__ = "symbolic_occurrences"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    scene_id: Mapped[int] = mapped_column(
        ForeignKey("scenes.id", ondelete="CASCADE"),
        nullable=False,
    )
    motif_id: Mapped[int] = mapped_column(
        ForeignKey("symbolic_motifs.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Occurrence details
    intensity: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )  # 0-10 scale
    
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Flags for analysis
    is_contrast: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_explicit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Metadata
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    scene: Mapped["Scene"] = relationship("Scene", back_populates="symbolic_occurrences")
    motif: Mapped["SymbolicMotif"] = relationship("SymbolicMotif", back_populates="occurrences")
    
    def __repr__(self) -> str:
        return f"<SymbolicOccurrence(id={self.id}, scene={self.scene_id}, intensity={self.intensity})>"
