"""CharacterMotifRelationship model - connects characters to symbolic motifs."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .character import Character
    from .symbolic_motif import SymbolicMotif


class CharacterMotifRelationship(Base, TimestampMixin):
    """Tracks a character's relationship to an abstract concept via symbolic motifs.
    
    This enables tracking character relationships to abstract themes like:
    - Food (obsession, comfort, control)
    - Authority (fear, respect, rebellion)
    - Nature (connection, fear, reverence)
    - Violence (attraction, revulsion, necessity)
    
    Uses the same slider-based attributes as character-to-character relationships,
    maintaining the "accumulation over assignment" principle. We track intensities
    and dynamics rather than rigid symbolic mappings.
    
    Attributes:
        id: Primary key
        character_id: The character with this relationship
        motif_id: The symbolic motif they relate to
        description: Notes on this character's relationship to the motif
        attributes: JSONB for relationship dynamics with sliders
            Example: {"obsession": 0.9, "fear": 0.3, "comfort": 0.8}
        is_primary: Is this a primary motif for this character?
        exclude_from_ai: If True, don't include in AI context
        metadata: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        character: The character
        motif: The symbolic motif
    """
    
    __tablename__ = "character_motif_relationships"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )
    motif_id: Mapped[int] = mapped_column(
        ForeignKey("symbolic_motifs.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Relationship details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationship dynamics (JSONB sliders)
    # Example: {"obsession": 0.9, "fear": 0.3, "comfort": 0.8, "control": 0.7}
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Flags
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Metadata
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    character: Mapped["Character"] = relationship("Character", back_populates="motif_relationships")
    motif: Mapped["SymbolicMotif"] = relationship("SymbolicMotif", back_populates="character_relationships")
    
    def __repr__(self) -> str:
        return f"<CharacterMotifRelationship(id={self.id}, character={self.character_id}, motif={self.motif_id})>"
