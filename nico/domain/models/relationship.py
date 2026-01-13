"""Relationship model - connections between characters."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .character import Character
    from .project import Project


class Relationship(Base, TimestampMixin):
    """A Relationship between two characters.
    
    Relationships define how characters are connected (sibling, spouse,
    enemy, etc.) and can have extensible attributes with slider values
    to describe relationship dynamics (loving, toxic, etc.).
    
    Attributes:
        id: Primary key
        project_id: Foreign key to parent project
        character_a_id: First character in relationship
        character_b_id: Second character in relationship
        relationship_type: Type of relationship (sibling, spouse, friend, etc.)
        description: Description of the relationship
        attributes: JSONB for relationship dynamics with sliders
            Example: {"loving": 0.8, "toxic": 0.2, "trust": 0.6}
        status: Current status (active, estranged, deceased, etc.)
        began_at: When relationship started
        ended_at: When relationship ended (if applicable)
        metadata: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        project: Parent project
    """
    
    __tablename__ = "relationships"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    character_a_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    character_b_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Relationship definition
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationship dynamics (JSONB sliders)
    # Example: {"loving": 0.8, "toxic": 0.2, "trust": 0.6, "competitive": 0.4}
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Status and timeline
    status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    began_at: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    ended_at: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Metadata
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project")
    
    def __repr__(self) -> str:
        return f"<Relationship(id={self.id}, type='{self.relationship_type}')>"
