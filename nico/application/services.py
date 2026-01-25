"""Application services for business logic."""
from typing import List, Optional

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
    Character,
    Location,
    Event,
    Relationship,
    Media,
    MediaAttachment,
)


class ProjectService:
    """Service for project-related operations."""
    
    def __init__(self, project_repo: ProjectRepository) -> None:
        self.project_repo = project_repo
    
    def list_projects(self) -> List[Project]:
        """Get all projects."""
        return self.project_repo.get_all()
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get project with full hierarchy."""
        return self.project_repo.get_by_id(project_id)
    
    def create_project(
        self,
        title: str,
        description: Optional[str] = None,
        author: Optional[str] = None,
    ) -> Project:
        """Create a new project."""
        project = Project(
            title=title,
            description=description,
            author=author,
        )
        return self.project_repo.create(project)


class SceneService:
    """Service for scene-related operations."""
    
    def __init__(self, scene_repo: SceneRepository) -> None:
        self.scene_repo = scene_repo
    
    def get_scene(self, scene_id: int) -> Optional[Scene]:
        """Get scene by ID."""
        return self.scene_repo.get_by_id(scene_id)
    
    def update_scene_content(self, scene_id: int, content: str, word_count: int) -> Optional[Scene]:
        """Update scene content and word count."""
        scene = self.scene_repo.get_by_id(scene_id)
        if scene:
            scene.content = content
            scene.word_count = word_count
            return self.scene_repo.update(scene)
        return None


class CharacterService:
    """Service for character-related operations."""
    
    def __init__(self, character_repo: CharacterRepository) -> None:
        self.character_repo = character_repo
    
    def list_characters(self, project_id: int) -> List[Character]:
        """Get all characters in a project."""
        return self.character_repo.get_all(project_id)
    
    def get_character(self, character_id: int) -> Optional[Character]:
        """Get character by ID."""
        return self.character_repo.get_by_id(character_id)
    
    def create_character(self, project_id: int, **kwargs) -> Character:
        """Create a new character."""
        character = Character(project_id=project_id, **kwargs)
        return self.character_repo.create(character)
    
    def update_character(self, character_id: int, **kwargs) -> Optional[Character]:
        """Update an existing character."""
        character = self.character_repo.get_by_id(character_id)
        if character:
            for key, value in kwargs.items():
                if hasattr(character, key):
                    setattr(character, key, value)
            return self.character_repo.update(character)
        return None
    
    def delete_character(self, character_id: int) -> bool:
        """Delete a character."""
        character = self.character_repo.get_by_id(character_id)
        if character:
            self.character_repo.delete(character_id)
            return True
        return False


class LocationService:
    """Service for location-related operations."""
    
    def __init__(self, location_repo: LocationRepository) -> None:
        self.location_repo = location_repo
    
    def list_locations(self, project_id: int) -> List[Location]:
        """Get all locations in a project."""
        return self.location_repo.get_all(project_id)
    
    def get_location(self, location_id: int) -> Optional[Location]:
        """Get location by ID."""
        return self.location_repo.get_by_id(location_id)
    
    def create_location(self, project_id: int, name: str, **kwargs) -> Location:
        """Create a new location."""
        location = Location(project_id=project_id, name=name, **kwargs)
        return self.location_repo.create(location)
    
    def update_location(self, location_id: int, **kwargs) -> Optional[Location]:
        """Update an existing location."""
        location = self.location_repo.get_by_id(location_id)
        if location:
            for key, value in kwargs.items():
                if hasattr(location, key):
                    setattr(location, key, value)
            return self.location_repo.update(location)
        return None
    
    def delete_location(self, location_id: int) -> bool:
        """Delete a location."""
        location = self.location_repo.get_by_id(location_id)
        if location:
            self.location_repo.delete(location_id)
            return True
        return False


class EventService:
    """Service for event-related operations."""
    
    def __init__(self, event_repo: EventRepository) -> None:
        self.event_repo = event_repo
    
    def list_events(self, project_id: int) -> List[Event]:
        """Get all events in a project, ordered by timeline."""
        return self.event_repo.get_all(project_id)
    
    def get_event(self, event_id: int) -> Optional[Event]:
        """Get event by ID."""
        return self.event_repo.get_by_id(event_id)
    
    def create_event(self, project_id: int, title: str, **kwargs) -> Event:
        """Create a new event."""
        event = Event(project_id=project_id, title=title, **kwargs)
        return self.event_repo.create(event)
    
    def update_event(self, event_id: int, **kwargs) -> Optional[Event]:
        """Update an existing event."""
        event = self.event_repo.get_by_id(event_id)
        if event:
            for key, value in kwargs.items():
                if hasattr(event, key):
                    setattr(event, key, value)
            return self.event_repo.update(event)
        return None
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event."""
        event = self.event_repo.get_by_id(event_id)
        if event:
            self.event_repo.delete(event_id)
            return True
        return False


class RelationshipService:
    """Service for relationship-related operations."""
    
    def __init__(self, relationship_repo: RelationshipRepository) -> None:
        self.relationship_repo = relationship_repo
    
    def list_relationships(self, project_id: int) -> List[Relationship]:
        """Get all relationships in a project."""
        return self.relationship_repo.get_all(project_id)
    
    def get_character_relationships(self, character_id: int) -> List[Relationship]:
        """Get all relationships involving a character."""
        return self.relationship_repo.get_by_character(character_id)
    
    def get_relationship(self, relationship_id: int) -> Optional[Relationship]:
        """Get relationship by ID."""
        return self.relationship_repo.get_by_id(relationship_id)
    
    def create_relationship(
        self,
        project_id: int,
        character_a_id: int,
        character_b_id: int,
        relationship_type: str,
        **kwargs
    ) -> Relationship:
        """Create a new relationship."""
        relationship = Relationship(
            project_id=project_id,
            character_a_id=character_a_id,
            character_b_id=character_b_id,
            relationship_type=relationship_type,
            **kwargs
        )
        return self.relationship_repo.create(relationship)
    
    def update_relationship(self, relationship_id: int, **kwargs) -> Optional[Relationship]:
        """Update an existing relationship."""
        relationship = self.relationship_repo.get_by_id(relationship_id)
        if relationship:
            for key, value in kwargs.items():
                if hasattr(relationship, key):
                    setattr(relationship, key, value)
            return self.relationship_repo.update(relationship)
        return None
    
    def delete_relationship(self, relationship_id: int) -> bool:
        """Delete a relationship."""
        relationship = self.relationship_repo.get_by_id(relationship_id)
        if relationship:
            self.relationship_repo.delete(relationship_id)
            return True
        return False


class MediaService:
    """Service for media library operations."""
    
    def __init__(self, session) -> None:
        self.session = session
    
    def list_media(self, project_id: int) -> List[Media]:
        """Get all media items in a project."""
        return self.session.query(Media).filter(
            Media.project_id == project_id
        ).order_by(Media.created_at.desc()).all()
    
    def get_media(self, media_id: int) -> Optional[Media]:
        """Get media item by ID."""
        return self.session.query(Media).filter(Media.id == media_id).first()
    
    def create_media(
        self,
        project_id: int,
        media_type: str,
        original_filename: str,
        file_path: str,
        mime_type: str,
        file_size: int,
        file_hash: str,
        **kwargs
    ) -> Media:
        """Create a new media item."""
        media = Media(
            project_id=project_id,
            media_type=media_type,
            original_filename=original_filename,
            file_path=file_path,
            mime_type=mime_type,
            file_size=file_size,
            file_hash=file_hash,
            **kwargs
        )
        self.session.add(media)
        self.session.commit()
        return media
    
    def update_media(self, media_id: int, **kwargs) -> Optional[Media]:
        """Update an existing media item."""
        media = self.get_media(media_id)
        if media:
            for key, value in kwargs.items():
                if hasattr(media, key):
                    setattr(media, key, value)
            self.session.commit()
        return media
    
    def delete_media(self, media_id: int) -> bool:
        """Delete a media item."""
        media = self.get_media(media_id)
        if media:
            self.session.delete(media)
            self.session.commit()
            return True
        return False
    
    def attach_media_to_entity(
        self,
        media_id: int,
        entity_type: str,
        entity_id: int,
        caption: Optional[str] = None,
        position: Optional[int] = None
    ) -> MediaAttachment:
        """Attach a media item to an entity."""
        attachment = MediaAttachment(
            media_id=media_id,
            entity_type=entity_type,
            entity_id=entity_id,
            caption=caption,
            position=position or 0,
        )
        self.session.add(attachment)
        self.session.commit()
        return attachment
    
    def get_entity_media(self, entity_type: str, entity_id: int) -> List[Media]:
        """Get all media attached to an entity."""
        attachments = self.session.query(MediaAttachment).filter(
            MediaAttachment.entity_type == entity_type,
            MediaAttachment.entity_id == entity_id
        ).order_by(MediaAttachment.position).all()
        
        return [att.media for att in attachments]
    
    def detach_media_from_entity(self, attachment_id: int) -> bool:
        """Remove a media attachment."""
        attachment = self.session.query(MediaAttachment).filter(
            MediaAttachment.id == attachment_id
        ).first()
        if attachment:
            self.session.delete(attachment)
            self.session.commit()
            return True
        return False
