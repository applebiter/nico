"""Location model - rich location entity."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project


class Location(Base, TimestampMixin):
    """A Location entity representing a place in the narrative.
    
    Locations can be as detailed as characters themselves, with rich
    descriptions, attributes, and metadata. They can be attached to
    scenes, events, and tracked throughout the narrative.
    
    Attributes:
        id: Primary key
        project_id: Foreign key to parent project
        name: Location name
        location_type: Type of location (city, building, planet, etc.)
        description: Detailed description of the location
        atmosphere: Mood or feeling of the location
        history: Historical background
        population: Population size/characteristics
        geography: Geographical features
        climate: Climate description
        culture: Cultural aspects
        economy: Economic characteristics
        government: Governmental structure
        attributes: JSONB for user-defined attributes with sliders
        coordinates: JSONB for lat/long or fictional coordinate system
        exclude_from_ai: If True, don't send this location to AI
        metadata: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        project: Parent project
    """
    
    __tablename__ = "locations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Core fields
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    location_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Rich descriptive fields
    atmosphere: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    population: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    geography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    climate: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    culture: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    economy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    government: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Extensible attributes (JSONB)
    # Example: {"danger_level": 0.7, "wealth": 0.4, "magic_intensity": 0.9}
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Coordinates (real or fictional)
    # Example: {"lat": 40.7128, "lng": -74.0060} or {"x": 1500, "y": 2300}
    coordinates: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # AI and metadata
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project")
    
    def __repr__(self) -> str:
        return f"<Location(id={self.id}, name='{self.name}')>"
