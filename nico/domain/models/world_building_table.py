"""World building table model - reusable random element tables."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project


class WorldBuildingTable(Base, TimestampMixin):
    """A table of random elements for world-building and content generation.
    
    These tables store CSV-like data that can be referenced in templates using
    tag interpolation (e.g., {character_trait:personality.positive}). Each table
    contains items that can be randomly selected during generation.
    
    Examples:
    - Character traits: brave, cowardly, ambitious, lazy
    - Location types: tavern, castle, forest clearing, cave
    - Weather conditions: sunny, stormy, foggy, scorching
    - Plot devices: betrayal, revelation, chase, confrontation
    
    Attributes:
        id: Primary key
        project_id: Foreign key to parent project
        table_name: Unique name for referencing in templates (e.g., "personality_traits")
        category: Organizational category (e.g., "character", "setting", "plot")
        description: What this table is for
        items: JSONB array of string items to select from
        weights: Optional JSONB array of selection weights (same length as items)
        tags: JSONB array of tags for filtering/organization
        exclude_from_ai: If True, don't send this table to AI
        meta: Flexible JSONB for additional data
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
        project: Parent project
    """
    
    __tablename__ = "world_building_tables"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Core fields
    table_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Data - array of items to select from
    # Example: ["brave", "cowardly", "ambitious", "cautious"]
    items: Mapped[list] = mapped_column(JSONB, nullable=False)
    
    # Optional weights for weighted random selection (same length as items)
    # Example: [2.0, 1.0, 1.5, 1.0] makes "brave" twice as likely as "cowardly"
    weights: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Tags for organization and filtering
    # Example: ["personality", "positive", "core_traits"]
    tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # AI and metadata
    exclude_from_ai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project")
    
    def __repr__(self) -> str:
        return f"<WorldBuildingTable(id={self.id}, name='{self.table_name}', items={len(self.items) if self.items else 0})>"
    
    def get_random_item(self, random_state=None) -> Optional[str]:
        """Get a random item from the table.
        
        Args:
            random_state: Optional random state for reproducibility
            
        Returns:
            Random item from the table, or None if table is empty
        """
        import random
        
        if not self.items:
            return None
        
        rng = random_state if random_state else random
        
        if self.weights and len(self.weights) == len(self.items):
            # Weighted selection
            return rng.choices(self.items, weights=self.weights, k=1)[0]
        else:
            # Uniform selection
            return rng.choice(self.items)
    
    def get_random_items(self, count: int, allow_duplicates: bool = False, random_state=None) -> list[str]:
        """Get multiple random items from the table.
        
        Args:
            count: Number of items to select
            allow_duplicates: If False, each item can only be selected once
            random_state: Optional random state for reproducibility
            
        Returns:
            List of random items
        """
        import random
        
        if not self.items:
            return []
        
        rng = random_state if random_state else random
        
        if allow_duplicates:
            if self.weights and len(self.weights) == len(self.items):
                return rng.choices(self.items, weights=self.weights, k=count)
            else:
                return rng.choices(self.items, k=count)
        else:
            # Sample without replacement
            actual_count = min(count, len(self.items))
            if self.weights and len(self.weights) == len(self.items):
                # Weighted sampling without replacement is complex, fallback to simple
                # TODO: Implement proper weighted sampling without replacement
                return rng.sample(self.items, actual_count)
            else:
                return rng.sample(self.items, actual_count)
