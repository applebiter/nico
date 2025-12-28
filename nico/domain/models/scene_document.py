"""SceneDocument domain model."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from .base import Entity


class SceneDocument(Entity):
    """
    The canonical JSON document containing a Scene's rich text content.
    
    This is a schema-driven document supporting:
    - Rich text marks (bold, italics, etc.)
    - Block structure (paragraphs, headings, lists)
    - Screenplay blocks (scene heading, action, character, dialogue, etc.)
    - Inline annotations (comments, highlights)
    - Inline entities (citations, cross-references, links)
    """

    def __init__(
        self,
        scene_id: UUID,
        content: Dict[str, Any],
        id: Optional[UUID] = None,
        rendered_text: Optional[str] = None,
        version: int = 1,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
    ):
        super().__init__(id)
        self.scene_id = scene_id
        self.content = content  # JSON structure (ProseMirror/TipTap document)
        self.rendered_text = rendered_text  # Plain text for search/preview
        self.version = version
        
        if created_at:
            self.created_at = created_at
        if modified_at:
            self.modified_at = modified_at

    def __repr__(self) -> str:
        text_preview = (self.rendered_text or "")[:50]
        return f"<SceneDocument(scene_id={self.scene_id}, version={self.version}, preview='{text_preview}...')>"


class SceneRevision(Entity):
    """
    A snapshot of a SceneDocument at a point in time.
    
    Revisions are created based on:
    - Time-based checkpoints (every N minutes)
    - Event-based (scene switch, export, AI rewrite)
    - Size-based (large change bursts)
    """

    def __init__(
        self,
        scene_id: UUID,
        content: Dict[str, Any],
        reason: str,
        id: Optional[UUID] = None,
        rendered_text: Optional[str] = None,
        version: int = 1,
        created_at: Optional[datetime] = None,
    ):
        super().__init__(id)
        self.scene_id = scene_id
        self.content = content
        self.rendered_text = rendered_text
        self.version = version
        self.reason = reason  # "autosave", "manual", "ai_rewrite", etc.
        
        if created_at:
            self.created_at = created_at

    def __repr__(self) -> str:
        return f"<SceneRevision(scene_id={self.scene_id}, version={self.version}, reason='{self.reason}')>"
