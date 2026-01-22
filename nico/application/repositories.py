"""Repository interfaces for data access."""
from abc import ABC, abstractmethod
from typing import List, Optional

from nico.domain.models import Project, Story, Chapter, Scene, Character, Location, Event, Relationship


class ProjectRepository(ABC):
    """Repository interface for Project operations."""
    
    @abstractmethod
    def get_all(self) -> List[Project]:
        """Get all projects."""
        pass
    
    @abstractmethod
    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        pass
    
    @abstractmethod
    def create(self, project: Project) -> Project:
        """Create a new project."""
        pass
    
    @abstractmethod
    def update(self, project: Project) -> Project:
        """Update an existing project."""
        pass
    
    @abstractmethod
    def delete(self, project_id: int) -> None:
        """Delete a project."""
        pass


class SceneRepository(ABC):
    """Repository interface for Scene operations."""
    
    @abstractmethod
    def get_by_id(self, scene_id: int) -> Optional[Scene]:
        """Get scene by ID."""
        pass
    
    @abstractmethod
    def get_by_chapter(self, chapter_id: int) -> List[Scene]:
        """Get all scenes in a chapter."""
        pass
    
    @abstractmethod
    def create(self, scene: Scene) -> Scene:
        """Create a new scene."""
        pass
    
    @abstractmethod
    def update(self, scene: Scene) -> Scene:
        """Update an existing scene."""
        pass
    
    @abstractmethod
    def delete(self, scene_id: int) -> None:
        """Delete a scene."""
        pass


class CharacterRepository(ABC):
    """Repository interface for Character operations."""
    
    @abstractmethod
    def get_all(self, project_id: int) -> List[Character]:
        """Get all characters in a project."""
        pass
    
    @abstractmethod
    def get_by_id(self, character_id: int) -> Optional[Character]:
        """Get character by ID."""
        pass
    
    @abstractmethod
    def create(self, character: Character) -> Character:
        """Create a new character."""
        pass
    
    @abstractmethod
    def update(self, character: Character) -> Character:
        """Update an existing character."""
        pass
    
    @abstractmethod
    def delete(self, character_id: int) -> None:
        """Delete a character."""
        pass


class LocationRepository(ABC):
    """Repository interface for Location operations."""
    
    @abstractmethod
    def get_all(self, project_id: int) -> List[Location]:
        """Get all locations in a project."""
        pass
    
    @abstractmethod
    def get_by_id(self, location_id: int) -> Optional[Location]:
        """Get location by ID."""
        pass
    
    @abstractmethod
    def create(self, location: Location) -> Location:
        """Create a new location."""
        pass
    
    @abstractmethod
    def update(self, location: Location) -> Location:
        """Update an existing location."""
        pass
    
    @abstractmethod
    def delete(self, location_id: int) -> None:
        """Delete a location."""
        pass


class EventRepository(ABC):
    """Repository interface for Event operations."""
    
    @abstractmethod
    def get_all(self, project_id: int) -> List[Event]:
        """Get all events in a project."""
        pass
    
    @abstractmethod
    def get_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID."""
        pass
    
    @abstractmethod
    def create(self, event: Event) -> Event:
        """Create a new event."""
        pass
    
    @abstractmethod
    def update(self, event: Event) -> Event:
        """Update an existing event."""
        pass
    
    @abstractmethod
    def delete(self, event_id: int) -> None:
        """Delete an event."""
        pass


class RelationshipRepository(ABC):
    """Repository interface for Relationship operations."""
    
    @abstractmethod
    def get_all(self, project_id: int) -> List[Relationship]:
        """Get all relationships in a project."""
        pass
    
    @abstractmethod
    def get_by_character(self, character_id: int) -> List[Relationship]:
        """Get all relationships involving a character."""
        pass
    
    @abstractmethod
    def get_by_id(self, relationship_id: int) -> Optional[Relationship]:
        """Get relationship by ID."""
        pass
    
    @abstractmethod
    def create(self, relationship: Relationship) -> Relationship:
        """Create a new relationship."""
        pass
    
    @abstractmethod
    def update(self, relationship: Relationship) -> Relationship:
        """Update an existing relationship."""
        pass
    
    @abstractmethod
    def delete(self, relationship_id: int) -> None:
        """Delete a relationship."""
        pass
