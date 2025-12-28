"""Scene domain model."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from .base import Entity


class Scene(Entity):
    """
    A Scene is the fundamental writing unit within a Chapter.
    
    Each Scene has a SceneDocument containing the actual content.
    Scenes maintain ordering via rank_key.
    """

    def __init__(
        self,
        chapter_id: UUID,
        title: str,
        rank_key: str,
        id: Optional[UUID] = None,
        synopsis: Optional[str] = None,
        status: str = "draft",
        pov_character_id: Optional[UUID] = None,
        scene_date: Optional[datetime] = None,
        word_count: int = 0,
        exclude_from_ai: bool = False,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
    ):
        super().__init__(id)
        self.chapter_id = chapter_id
        self.title = title
        self.rank_key = rank_key
        self.synopsis = synopsis
        self.status = status
        self.pov_character_id = pov_character_id
        self.scene_date = scene_date
        self.word_count = word_count
        self.exclude_from_ai = exclude_from_ai
        
        if created_at:
            self.created_at = created_at
        if modified_at:
            self.modified_at = modified_at

    def __repr__(self) -> str:
        return f"<Scene(id={self.id}, title='{self.title}', words={self.word_count})>"
