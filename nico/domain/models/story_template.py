"""Story template model - macro-level story structure templates."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project


class StoryTemplate(Base, TimestampMixin):
    """A macro-level template for story structure.
    
    Story templates define the high-level structure of a story: number of acts,
    chapters, major beats, and structural requirements. They can be genre-specific
    (mystery thriller, romance, hero's journey) or custom.
    
    Attributes:
        id: Primary key
        project_id: Foreign key to parent project (null for global templates)
        name: Template name (e.g., "Mystery Thriller", "Three Act Structure")
        genre: Genre classification
        description: What this template is for
        target_word_count: Target total word count
        act_structure: JSONB defining acts and their chapter ranges
        chapter_structure: JSONB defining chapter requirements
        required_beats: JSONB array of story beats with timing
        required_scenes: JSONB array of required scene types
        symbolic_themes: JSONB array of recommended themes
        is_public: If True, available to all projects
        exclude_from_ai: If True, don't send this template to AI
        meta: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        project: Parent project (if not public)
    """
    
    __tablename__ = "story_templates"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,  # Null for global templates
    )
    
    # Core fields
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Target metrics
    target_word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Act structure
    # Example: [
    #   {"act": 1, "name": "Setup", "chapters": [1, 5], "description": "Introduce world and conflict"},
    #   {"act": 2, "name": "Confrontation", "chapters": [6, 15], "description": "Rising tension"},
    #   {"act": 3, "name": "Resolution", "chapters": [16, 20], "description": "Climax and denouement"}
    # ]
    act_structure: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Chapter structure
    # Example: {
    #   "total_chapters": 20,
    #   "chapter_word_range": [2500, 4000],
    #   "chapter_templates": {
    #     "1": {"type": "opening", "required_elements": ["hook", "world_intro"]},
    #     "5": {"type": "plot_twist", "required_elements": ["revelation", "stakes_raise"]}
    #   }
    # }
    chapter_structure: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Required story beats with normalized timing (0.0 to 1.0)
    # Example: [
    #   {"name": "Inciting Incident", "position": 0.12, "description": "Event that kicks off the story"},
    #   {"name": "Midpoint", "position": 0.50, "description": "Major revelation or reversal"},
    #   {"name": "Dark Night", "position": 0.75, "description": "All seems lost"},
    #   {"name": "Climax", "position": 0.90, "description": "Final confrontation"}
    # ]
    required_beats: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Required scene types
    # Example: [
    #   {"type": "crime_discovery", "act": 1, "description": "Detective discovers the crime"},
    #   {"type": "false_accusation", "act": 2, "description": "Wrong suspect arrested"},
    #   {"type": "revelation", "act": 3, "description": "True culprit revealed"}
    # ]
    required_scenes: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Recommended symbolic themes
    # Example: ["justice vs revenge", "truth vs lies", "redemption"]
    symbolic_themes: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Visibility and AI
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project")
    
    def __repr__(self) -> str:
        return f"<StoryTemplate(id={self.id}, name='{self.name}', genre='{self.genre}')>"
    
    def get_chapter_count(self) -> int:
        """Get the total number of chapters in this template."""
        if self.chapter_structure and "total_chapters" in self.chapter_structure:
            return self.chapter_structure["total_chapters"]
        return 0
    
    def get_beat_at_position(self, position: float) -> Optional[dict]:
        """Get the story beat closest to a given position (0.0 to 1.0)."""
        if not self.required_beats:
            return None
        
        closest_beat = None
        min_distance = float('inf')
        
        for beat in self.required_beats:
            if "position" in beat:
                distance = abs(beat["position"] - position)
                if distance < min_distance:
                    min_distance = distance
                    closest_beat = beat
        
        return closest_beat
