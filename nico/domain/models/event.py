"""Event model - timeline events binding characters and locations."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project


class Event(Base, TimestampMixin):
    """An Event in the narrative timeline.
    
    Events bind characters and locations in time, tracking what happens
    when and where. They support both precise timestamps and relative
    positioning for flexible timeline management.
    
    Attributes:
        id: Primary key
        project_id: Foreign key to parent project
        title: Event name/title
        description: Detailed description of the event
        event_type: Type of event (battle, meeting, birth, etc.)
        occurred_at: When the event occurred (timestamp)
        ended_at: When the event ended (for duration events)
        timeline_position: Relative position for ordering (integer)
        duration: Duration description (e.g., "3 days", "2 hours")
        scope: Scope of the event (personal, regional, global, etc.)
        significance: Importance level or description
        outcome: Result or consequence of the event
        participants: JSONB list of character IDs involved
        locations: JSONB list of location IDs where event occurred
        exclude_from_ai: If True, don't send this event to AI
        metadata: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        project: Parent project
    """
    
    __tablename__ = "events"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Core fields
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timeline fields
    occurred_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    timeline_position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Event characteristics
    scope: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    significance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships to characters and locations (JSONB arrays)
    # Example: {"character_ids": [1, 2, 5], "roles": {"1": "protagonist", "2": "witness"}}
    participants: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Example: {"location_ids": [3, 7], "primary_location_id": 3}
    locations: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # AI and metadata
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project")
    
    def __repr__(self) -> str:
        return f"<Event(id={self.id}, title='{self.title}')>"
