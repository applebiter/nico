"""Scene template model - tag interpolation templates for scene content."""
from typing import TYPE_CHECKING, Optional
import re

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project


class SceneTemplate(Base, TimestampMixin):
    """A scene content template with tag interpolation.
    
    Scene templates use tag-based substitution to generate varied content from
    world-building tables. Tags follow the format {tag_name} or {tag_name:table.category}.
    
    Examples:
    - Simple: "{protagonist} entered the {location} and saw {detail}."
    - With table refs: "{protagonist} felt {emotion:feelings.negative} about {mcguffin}."
    
    Attributes:
        id: Primary key
        project_id: Foreign key to parent project (null for global templates)
        name: Template name
        scene_type: Type of scene (action, dialogue, description, transition)
        description: What this template generates
        template_text: The template with {tags} for interpolation
        required_tags: JSONB array of required tag names
        table_mappings: JSONB dict mapping tags to WorldBuildingTable references
        example_output: Example of what this template generates
        is_public: If True, available to all projects
        exclude_from_ai: If True, don't send this template to AI
        meta: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        project: Parent project (if not public)
    """
    
    __tablename__ = "scene_templates"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,  # Null for global templates
    )
    
    # Core fields
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    scene_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Template content
    template_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Required tags (parsed from template_text)
    # Example: ["protagonist", "location", "emotion", "mcguffin"]
    required_tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Mapping of tags to WorldBuildingTable references
    # Example: {
    #   "emotion": "feelings.negative",
    #   "location": "locations.indoor",
    #   "detail": "suspicious_details"
    # }
    table_mappings: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Example output for reference
    example_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Visibility and AI
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project")
    
    def __repr__(self) -> str:
        return f"<SceneTemplate(id={self.id}, name='{self.name}', type='{self.scene_type}')>"
    
    def extract_tags(self) -> list[str]:
        """Extract all {tags} from the template text.
        
        Returns:
            List of tag names found in the template
        """
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, self.template_text)
        
        # Remove table references (e.g., "emotion:feelings.negative" -> "emotion")
        tags = []
        for match in matches:
            if ':' in match:
                tag_name = match.split(':')[0]
            else:
                tag_name = match
            tags.append(tag_name)
        
        return list(set(tags))  # Remove duplicates
    
    def interpolate(self, values: dict[str, str]) -> str:
        """Interpolate values into the template.
        
        Args:
            values: Dict mapping tag names to their replacement values
            
        Returns:
            Template with tags replaced by values
        """
        result = self.template_text
        
        for tag, value in values.items():
            # Replace {tag} and {tag:table.ref} patterns
            result = re.sub(rf'\{{{tag}(?::[^}}]+)?\}}', value, result)
        
        return result
    
    def get_table_reference(self, tag: str) -> Optional[str]:
        """Get the WorldBuildingTable reference for a tag.
        
        Args:
            tag: Tag name
            
        Returns:
            Table reference (e.g., "feelings.negative") or None
        """
        if not self.table_mappings:
            return None
        
        return self.table_mappings.get(tag)
    
    def validate_template(self) -> tuple[bool, Optional[str]]:
        """Validate that the template is well-formed.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for unmatched braces
        open_count = self.template_text.count('{')
        close_count = self.template_text.count('}')
        
        if open_count != close_count:
            return False, f"Unmatched braces: {open_count} opening, {close_count} closing"
        
        # Check that all tags have corresponding table mappings or are simple tags
        tags = self.extract_tags()
        if self.table_mappings:
            for tag in tags:
                # Tags can be in template as {tag} even without mappings
                # (they'd be provided at interpolation time)
                pass
        
        return True, None
