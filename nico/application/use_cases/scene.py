"""Use cases for Scene operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from nico.domain.models import Scene, SceneDocument, SceneRevision
from nico.domain.repositories import ISceneDocumentRepository, ISceneRepository
from nico.domain.services.ranking import generate_rank_key


class CreateSceneUseCase:
    """Create a new scene in a chapter."""

    def __init__(self, scene_repo: ISceneRepository, doc_repo: ISceneDocumentRepository):
        self.scene_repo = scene_repo
        self.doc_repo = doc_repo

    def execute(
        self,
        chapter_id: UUID,
        title: str,
        synopsis: Optional[str] = None,
        status: str = "draft",
        after_scene_id: Optional[UUID] = None,
    ) -> Scene:
        """
        Create a new scene with an empty document.
        
        Args:
            chapter_id: Parent chapter ID
            title: Scene title
            synopsis: Optional synopsis
            status: Scene status (default: "draft")
            after_scene_id: Optional ID of scene to insert after (None = append to end)
            
        Returns:
            Created Scene entity
        """
        scenes = self.scene_repo.get_by_chapter(chapter_id)
        
        if not scenes:
            rank_key = generate_rank_key()
        elif after_scene_id is None:
            last_rank = scenes[-1].rank_key
            rank_key = generate_rank_key(before=last_rank)
        else:
            after_idx = next((i for i, s in enumerate(scenes) if s.id == after_scene_id), None)
            if after_idx is None:
                raise ValueError(f"Scene {after_scene_id} not found in chapter")
            
            before_rank = scenes[after_idx].rank_key
            after_rank = scenes[after_idx + 1].rank_key if after_idx + 1 < len(scenes) else None
            rank_key = generate_rank_key(before=before_rank, after=after_rank)

        scene = Scene(
            chapter_id=chapter_id,
            title=title,
            rank_key=rank_key,
            synopsis=synopsis,
            status=status,
        )

        scene = self.scene_repo.create(scene)
        
        # Create empty document
        document = SceneDocument(
            scene_id=scene.id,
            content={"type": "doc", "content": []},  # Empty ProseMirror-style document
            rendered_text="",
        )
        self.doc_repo.create(document)
        
        return scene


class ListScenesUseCase:
    """List all scenes in a chapter."""

    def __init__(self, scene_repo: ISceneRepository):
        self.scene_repo = scene_repo

    def execute(self, chapter_id: UUID) -> List[Scene]:
        """
        List all scenes in a chapter, ordered by rank_key.
        
        Args:
            chapter_id: Chapter ID
            
        Returns:
            List of Scene entities
        """
        return self.scene_repo.get_by_chapter(chapter_id)


class GetSceneUseCase:
    """Get a single scene by ID."""

    def __init__(self, scene_repo: ISceneRepository):
        self.scene_repo = scene_repo

    def execute(self, scene_id: UUID) -> Optional[Scene]:
        """
        Get a scene by ID.
        
        Args:
            scene_id: Scene ID
            
        Returns:
            Scene entity or None if not found
        """
        return self.scene_repo.get_by_id(scene_id)


class UpdateSceneUseCase:
    """Update scene metadata."""

    def __init__(self, scene_repo: ISceneRepository):
        self.scene_repo = scene_repo

    def execute(
        self,
        scene_id: UUID,
        title: Optional[str] = None,
        synopsis: Optional[str] = None,
        status: Optional[str] = None,
        pov_character_id: Optional[UUID] = None,
        scene_date: Optional[datetime] = None,
        exclude_from_ai: Optional[bool] = None,
    ) -> Scene:
        """
        Update scene metadata.
        
        Args:
            scene_id: Scene ID
            title: New title (optional)
            synopsis: New synopsis (optional)
            status: New status (optional)
            pov_character_id: New POV character (optional)
            scene_date: New scene date (optional)
            exclude_from_ai: New AI exclusion flag (optional)
            
        Returns:
            Updated Scene entity
        """
        scene = self.scene_repo.get_by_id(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        if title is not None:
            scene.title = title
        if synopsis is not None:
            scene.synopsis = synopsis
        if status is not None:
            scene.status = status
        if pov_character_id is not None:
            scene.pov_character_id = pov_character_id
        if scene_date is not None:
            scene.scene_date = scene_date
        if exclude_from_ai is not None:
            scene.exclude_from_ai = exclude_from_ai

        return self.scene_repo.update(scene)


class UpdateSceneDocumentUseCase:
    """Update scene document content."""

    def __init__(self, scene_repo: ISceneRepository, doc_repo: ISceneDocumentRepository):
        self.scene_repo = scene_repo
        self.doc_repo = doc_repo

    def execute(
        self,
        scene_id: UUID,
        content: dict,
        rendered_text: str,
        word_count: int,
        create_revision: bool = False,
        revision_reason: str = "autosave",
    ) -> SceneDocument:
        """
        Update scene document content (autosave).
        
        Args:
            scene_id: Scene ID
            content: New document content (ProseMirror JSON)
            rendered_text: Plain text rendering
            word_count: Word count
            create_revision: Whether to create a revision snapshot
            revision_reason: Reason for revision (if creating one)
            
        Returns:
            Updated SceneDocument entity
        """
        document = self.doc_repo.get_by_scene_id(scene_id)
        if not document:
            raise ValueError(f"Document for scene {scene_id} not found")

        # Create revision if requested
        if create_revision:
            revision = SceneRevision(
                scene_id=scene_id,
                content=document.content,
                rendered_text=document.rendered_text,
                version=document.version,
                reason=revision_reason,
            )
            self.doc_repo.create_revision(revision)

        # Update document
        document.content = content
        document.rendered_text = rendered_text
        document.version += 1
        document = self.doc_repo.update(document)

        # Update scene word count
        scene = self.scene_repo.get_by_id(scene_id)
        if scene:
            scene.word_count = word_count
            self.scene_repo.update(scene)

        return document


class GetSceneDocumentUseCase:
    """Retrieve scene document."""

    def __init__(self, doc_repo: ISceneDocumentRepository):
        self.doc_repo = doc_repo

    def execute(self, scene_id: UUID) -> Optional[SceneDocument]:
        """
        Get scene document.
        
        Args:
            scene_id: Scene ID
            
        Returns:
            SceneDocument entity or None
        """
        return self.doc_repo.get_by_scene_id(scene_id)


class GetSceneRevisionsUseCase:
    """Retrieve scene revision history."""

    def __init__(self, doc_repo: ISceneDocumentRepository):
        self.doc_repo = doc_repo

    def execute(self, scene_id: UUID, limit: Optional[int] = 50) -> List[SceneRevision]:
        """
        Get scene revisions.
        
        Args:
            scene_id: Scene ID
            limit: Maximum number of revisions to return
            
        Returns:
            List of SceneRevision entities, most recent first
        """
        return self.doc_repo.get_revisions(scene_id, limit)


class ReorderSceneUseCase:
    """Reorder a scene within its chapter."""

    def __init__(self, scene_repo: ISceneRepository):
        self.scene_repo = scene_repo

    def execute(self, scene_id: UUID, after_scene_id: Optional[UUID]) -> Scene:
        """
        Move a scene to a new position.
        
        Args:
            scene_id: Scene to move
            after_scene_id: Scene to insert after (None = move to beginning)
            
        Returns:
            Updated Scene entity with new rank_key
        """
        scene = self.scene_repo.get_by_id(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        scenes = self.scene_repo.get_by_chapter(scene.chapter_id)
        other_scenes = [s for s in scenes if s.id != scene_id]

        if not other_scenes:
            return scene

        if after_scene_id is None:
            first_rank = other_scenes[0].rank_key
            scene.rank_key = generate_rank_key(after=first_rank)
        else:
            after_idx = next((i for i, s in enumerate(other_scenes) if s.id == after_scene_id), None)
            if after_idx is None:
                raise ValueError(f"Scene {after_scene_id} not found")
            
            before_rank = other_scenes[after_idx].rank_key
            after_rank = other_scenes[after_idx + 1].rank_key if after_idx + 1 < len(other_scenes) else None
            scene.rank_key = generate_rank_key(before=before_rank, after=after_rank)

        return self.scene_repo.update(scene)


class DeleteSceneUseCase:
    """Delete a scene and its document."""

    def __init__(self, scene_repo: ISceneRepository):
        self.scene_repo = scene_repo

    def execute(self, scene_id: UUID) -> None:
        """
        Delete a scene.
        
        Args:
            scene_id: Scene ID
        """
        scene = self.scene_repo.get_by_id(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        self.scene_repo.delete(scene_id)
