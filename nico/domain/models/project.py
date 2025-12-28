"""Project domain model."""

from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from .base import Entity


class Project(Entity):
    """
    Root entity representing a writing project.
    
    A Project is a folder containing:
    - project.sqlite3 (database)
    - media/ (managed binaries)
    - chroma/ (vector database, if used)
    - exports/ (optional)
    - cache/ (optional)
    """

    def __init__(
        self,
        name: str,
        path: Path,
        id: Optional[UUID] = None,
        description: Optional[str] = None,
        author: Optional[str] = None,
        bibliography_style: str = "MLA",
        local_only_ai: bool = True,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
    ):
        super().__init__(id)
        self.name = name
        self.path = path
        self.description = description
        self.author = author
        self.bibliography_style = bibliography_style
        self.local_only_ai = local_only_ai
        
        if created_at:
            self.created_at = created_at
        if modified_at:
            self.modified_at = modified_at

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"
