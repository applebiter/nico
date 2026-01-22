"""SQLAlchemy implementation of repositories."""
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from nico.application.repositories import (
    ProjectRepository,
    SceneRepository,
    CharacterRepository,
    LocationRepository,
    EventRepository,
    RelationshipRepository,
)
from nico.domain.models import (
    Project,
    Scene,
    Story,
    Chapter,
    Character,
    Location,
    Event,
    Relationship,
)


class SQLAlchemyProjectRepository(ProjectRepository):
    """SQLAlchemy implementation of ProjectRepository."""
    
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def get_all(self) -> List[Project]:
        """Get all projects with their stories preloaded."""
        return self.session.query(Project).options(
            joinedload(Project.stories)
        ).all()
    
    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID with full hierarchy loaded."""
        return self.session.query(Project).options(
            joinedload(Project.stories).joinedload(Story.chapters).joinedload(Chapter.scenes)
        ).filter(Project.id == project_id).first()
    
    def create(self, project: Project) -> Project:
        """Create a new project."""
        self.session.add(project)
        self.session.flush()
        return project
    
    def update(self, project: Project) -> Project:
        """Update an existing project."""
        self.session.merge(project)
        self.session.flush()
        return project
    
    def delete(self, project_id: int) -> None:
        """Delete a project."""
        project = self.get_by_id(project_id)
        if project:
            self.session.delete(project)
            self.session.flush()


class SQLAlchemySceneRepository(SceneRepository):
    """SQLAlchemy implementation of SceneRepository."""
    
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def get_by_id(self, scene_id: int) -> Optional[Scene]:
        """Get scene by ID."""
        return self.session.query(Scene).filter(Scene.id == scene_id).first()
    
    def get_by_chapter(self, chapter_id: int) -> List[Scene]:
        """Get all scenes in a chapter."""
        return self.session.query(Scene).filter(
            Scene.chapter_id == chapter_id
        ).order_by(Scene.position).all()
    
    def create(self, scene: Scene) -> Scene:
        """Create a new scene."""
        self.session.add(scene)
        self.session.flush()
        return scene
    
    def update(self, scene: Scene) -> Scene:
        """Update an existing scene."""
        self.session.merge(scene)
        self.session.flush()
        return scene
    
    def delete(self, scene_id: int) -> None:
        """Delete a scene."""
        scene = self.get_by_id(scene_id)
        if scene:
            self.session.delete(scene)
            self.session.flush()


class SQLAlchemyCharacterRepository(CharacterRepository):
    """SQLAlchemy implementation of CharacterRepository."""
    
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def get_all(self, project_id: int) -> List[Character]:
        """Get all characters in a project."""
        return self.session.query(Character).filter(
            Character.project_id == project_id
        ).order_by(Character.first_name, Character.last_name).all()
    
    def get_by_id(self, character_id: int) -> Optional[Character]:
        """Get character by ID."""
        return self.session.query(Character).filter(Character.id == character_id).first()
    
    def create(self, character: Character) -> Character:
        """Create a new character."""
        self.session.add(character)
        self.session.flush()
        return character
    
    def update(self, character: Character) -> Character:
        """Update an existing character."""
        self.session.merge(character)
        self.session.flush()
        return character
    
    def delete(self, character_id: int) -> None:
        """Delete a character."""
        character = self.get_by_id(character_id)
        if character:
            self.session.delete(character)
            self.session.flush()


class SQLAlchemyLocationRepository(LocationRepository):
    """SQLAlchemy implementation of LocationRepository."""
    
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def get_all(self, project_id: int) -> List[Location]:
        """Get all locations in a project."""
        return self.session.query(Location).filter(
            Location.project_id == project_id
        ).order_by(Location.name).all()
    
    def get_by_id(self, location_id: int) -> Optional[Location]:
        """Get location by ID."""
        return self.session.query(Location).filter(Location.id == location_id).first()
    
    def create(self, location: Location) -> Location:
        """Create a new location."""
        self.session.add(location)
        self.session.flush()
        return location
    
    def update(self, location: Location) -> Location:
        """Update an existing location."""
        self.session.merge(location)
        self.session.flush()
        return location
    
    def delete(self, location_id: int) -> None:
        """Delete a location."""
        location = self.get_by_id(location_id)
        if location:
            self.session.delete(location)
            self.session.flush()


class SQLAlchemyEventRepository(EventRepository):
    """SQLAlchemy implementation of EventRepository."""
    
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def get_all(self, project_id: int) -> List[Event]:
        """Get all events in a project."""
        return self.session.query(Event).filter(
            Event.project_id == project_id
        ).order_by(Event.timeline_position, Event.occurred_at).all()
    
    def get_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID."""
        return self.session.query(Event).filter(Event.id == event_id).first()
    
    def create(self, event: Event) -> Event:
        """Create a new event."""
        self.session.add(event)
        self.session.flush()
        return event
    
    def update(self, event: Event) -> Event:
        """Update an existing event."""
        self.session.merge(event)
        self.session.flush()
        return event
    
    def delete(self, event_id: int) -> None:
        """Delete an event."""
        event = self.get_by_id(event_id)
        if event:
            self.session.delete(event)
            self.session.flush()


class SQLAlchemyRelationshipRepository(RelationshipRepository):
    """SQLAlchemy implementation of RelationshipRepository."""
    
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def get_all(self, project_id: int) -> List[Relationship]:
        """Get all relationships in a project."""
        return self.session.query(Relationship).filter(
            Relationship.project_id == project_id
        ).all()
    
    def get_by_character(self, character_id: int) -> List[Relationship]:
        """Get all relationships involving a character."""
        return self.session.query(Relationship).filter(
            (Relationship.character_a_id == character_id) |
            (Relationship.character_b_id == character_id)
        ).all()
    
    def get_by_id(self, relationship_id: int) -> Optional[Relationship]:
        """Get relationship by ID."""
        return self.session.query(Relationship).filter(
            Relationship.id == relationship_id
        ).first()
    
    def create(self, relationship: Relationship) -> Relationship:
        """Create a new relationship."""
        self.session.add(relationship)
        self.session.flush()
        return relationship
    
    def update(self, relationship: Relationship) -> Relationship:
        """Update an existing relationship."""
        self.session.merge(relationship)
        self.session.flush()
        return relationship
    
    def delete(self, relationship_id: int) -> None:
        """Delete a relationship."""
        relationship = self.get_by_id(relationship_id)
        if relationship:
            self.session.delete(relationship)
            self.session.flush()
