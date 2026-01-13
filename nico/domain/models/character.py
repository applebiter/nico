"""Character model - detailed character entity with extensible traits."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project


class Character(Base, TimestampMixin):
    """A Character entity with detailed attributes and extensible traits.
    
    Characters are complex entities that can be attached to scenes, events,
    and tracked throughout the narrative. Core attributes are normalized fields,
    while user-defined traits and psychological profiles use JSONB for flexibility.
    
    Attributes:
        id: Primary key
        project_id: Foreign key to parent project
        title: Title (Mr., Dr., etc.)
        honorific: Honorific prefix
        first_name: Given name
        middle_names: Middle name(s)
        last_name: Family name
        nickname: Preferred name or alias
        gender: Gender identity
        sex: Biological sex
        ethnicity: Ethnic background
        race: Racial identity
        tribe_or_clan: Tribal or clan affiliation
        nationality: National origin
        religion: Religious affiliation
        occupation: Current occupation
        education: Educational background
        marital_status: Marital status
        has_children: Whether character has children
        date_of_birth: Birth date
        date_of_death: Death date (if applicable)
        physical_description: Physical appearance details
        myers_briggs: MBTI personality type
        enneagram: Enneagram type
        wounds: Emotional/psychological wounds
        traits: JSONB for user-defined trait sliders (e.g., {"brave": 0.8, "loyal": 0.6})
        psychological_profile: JSONB for additional psychological attributes
        exclude_from_ai: If True, don't send this character to AI
        metadata: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        project: Parent project
    """
    
    __tablename__ = "characters"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Core name fields
    title: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    honorific: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    middle_names: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    nickname: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Identity attributes
    gender: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sex: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ethnicity: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    race: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tribe_or_clan: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    religion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Life circumstances
    occupation: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    education: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    marital_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    has_children: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Timeline
    date_of_birth: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    date_of_death: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    
    # Description and psychology
    physical_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    myers_briggs: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    enneagram: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    wounds: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Extensible traits and attributes (JSONB)
    # Example: {"brave": 0.8, "loyal": 0.6, "impulsive": 0.3}
    traits: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Additional psychological data
    # Example: {"strengths": ["leadership", "empathy"], "weaknesses": ["pride"]}
    psychological_profile: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # AI and metadata
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project")
    
    def __repr__(self) -> str:
        name = self.nickname or self.first_name or "Unnamed"
        return f"<Character(id={self.id}, name='{name}')>"
