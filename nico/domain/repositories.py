"""Repository interfaces for domain entities."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from nico.domain.models import (
    Chapter,
    Character,
    CharacterTrait,
    Project,
    Scene,
    SceneDocument,
    SceneRevision,
    Story,
)


class IProjectRepository(ABC):
    """Repository interface for Project entities."""

    @abstractmethod
    def create(self, project: Project) -> Project:
        """Create a new project."""
        pass

    @abstractmethod
    def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Get a project by ID."""
        pass

    @abstractmethod
    def get_by_path(self, path: Path) -> Optional[Project]:
        """Get a project by its folder path."""
        pass

    @abstractmethod
    def update(self, project: Project) -> Project:
        """Update an existing project."""
        pass

    @abstractmethod
    def delete(self, project_id: UUID) -> None:
        """Delete a project."""
        pass


class IStoryRepository(ABC):
    """Repository interface for Story entities."""

    @abstractmethod
    def create(self, story: Story) -> Story:
        """Create a new story."""
        pass

    @abstractmethod
    def get_by_id(self, story_id: UUID) -> Optional[Story]:
        """Get a story by ID."""
        pass

    @abstractmethod
    def get_by_project(self, project_id: UUID) -> List[Story]:
        """Get all stories in a project, ordered by rank_key."""
        pass

    @abstractmethod
    def update(self, story: Story) -> Story:
        """Update an existing story."""
        pass

    @abstractmethod
    def delete(self, story_id: UUID) -> None:
        """Delete a story."""
        pass


class IChapterRepository(ABC):
    """Repository interface for Chapter entities."""

    @abstractmethod
    def create(self, chapter: Chapter) -> Chapter:
        """Create a new chapter."""
        pass

    @abstractmethod
    def get_by_id(self, chapter_id: UUID) -> Optional[Chapter]:
        """Get a chapter by ID."""
        pass

    @abstractmethod
    def get_by_story(self, story_id: UUID) -> List[Chapter]:
        """Get all chapters in a story, ordered by rank_key."""
        pass

    @abstractmethod
    def update(self, chapter: Chapter) -> Chapter:
        """Update an existing chapter."""
        pass

    @abstractmethod
    def delete(self, chapter_id: UUID) -> None:
        """Delete a chapter."""
        pass


class ISceneRepository(ABC):
    """Repository interface for Scene entities."""

    @abstractmethod
    def create(self, scene: Scene) -> Scene:
        """Create a new scene."""
        pass

    @abstractmethod
    def get_by_id(self, scene_id: UUID) -> Optional[Scene]:
        """Get a scene by ID."""
        pass

    @abstractmethod
    def get_by_chapter(self, chapter_id: UUID) -> List[Scene]:
        """Get all scenes in a chapter, ordered by rank_key."""
        pass

    @abstractmethod
    def update(self, scene: Scene) -> Scene:
        """Update an existing scene."""
        pass

    @abstractmethod
    def delete(self, scene_id: UUID) -> None:
        """Delete a scene."""
        pass


class ISceneDocumentRepository(ABC):
    """Repository interface for SceneDocument entities."""

    @abstractmethod
    def create(self, document: SceneDocument) -> SceneDocument:
        """Create a new scene document."""
        pass

    @abstractmethod
    def get_by_scene_id(self, scene_id: UUID) -> Optional[SceneDocument]:
        """Get the document for a scene."""
        pass

    @abstractmethod
    def update(self, document: SceneDocument) -> SceneDocument:
        """Update an existing scene document."""
        pass

    @abstractmethod
    def create_revision(self, revision: SceneRevision) -> SceneRevision:
        """Create a revision snapshot."""
        pass

    @abstractmethod
    def get_revisions(self, scene_id: UUID, limit: Optional[int] = None) -> List[SceneRevision]:
        """Get revisions for a scene, most recent first."""
        pass


class ICharacterRepository(ABC):
    """Repository interface for Character entities."""

    @abstractmethod
    def create(self, character: Character) -> Character:
        """Create a new character."""
        pass

    @abstractmethod
    def get_by_id(self, character_id: UUID) -> Optional[Character]:
        """Get a character by ID."""
        pass

    @abstractmethod
    def get_by_project(self, project_id: UUID) -> List[Character]:
        """Get all characters in a project."""
        pass

    @abstractmethod
    def update(self, character: Character) -> Character:
        """Update an existing character."""
        pass

    @abstractmethod
    def delete(self, character_id: UUID) -> None:
        """Delete a character."""
        pass

    @abstractmethod
    def add_trait(self, trait: CharacterTrait) -> CharacterTrait:
        """Add a trait to a character."""
        pass

    @abstractmethod
    def get_traits(self, character_id: UUID) -> List[CharacterTrait]:
        """Get all traits for a character, ordered by position."""
        pass

    @abstractmethod
    def update_trait(self, trait: CharacterTrait) -> CharacterTrait:
        """Update a character trait."""
        pass

    @abstractmethod
    def delete_trait(self, trait_id: UUID) -> None:
        """Delete a character trait."""
        pass
