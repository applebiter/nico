"""Chapter domain model."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from .base import Entity


class Chapter(Entity):
    """
    A Chapter is a subdivision within a Story.
    
    Chapters contain Scenes and maintain ordering via rank_key.
    """

    def __init__(
        self,
        story_id: UUID,
        title: str,
        rank_key: str,
        id: Optional[UUID] = None,
        synopsis: Optional[str] = None,
        status: str = "draft",
        exclude_from_ai: bool = False,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
    ):
        super().__init__(id)
        self.story_id = story_id
        self.title = title
        self.rank_key = rank_key
        self.synopsis = synopsis
        self.status = status
        self.exclude_from_ai = exclude_from_ai
        
        if created_at:
            self.created_at = created_at
        if modified_at:
            self.modified_at = modified_at

    def __repr__(self) -> str:
        return f"<Chapter(id={self.id}, title='{self.title}')>"
