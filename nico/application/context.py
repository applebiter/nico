"""Application context and dependency injection."""
from typing import Optional

from sqlalchemy.orm import Session

from nico.infrastructure.database import DatabaseConfig, init_db, settings
from nico.infrastructure.database.repositories import (
    SQLAlchemyProjectRepository,
    SQLAlchemySceneRepository,
    SQLAlchemyCharacterRepository,
    SQLAlchemyLocationRepository,
    SQLAlchemyEventRepository,
    SQLAlchemyRelationshipRepository,
)
from nico.application.services import (
    ProjectService,
    SceneService,
    CharacterService,
    LocationService,
    EventService,
    RelationshipService,
)
from nico.application.generators import StoryGenerator
from nico.preferences import get_preferences
from nico.ai.manager import initialize_team_from_config


class AppContext:
    """Application context managing database and services."""
    
    def __init__(self) -> None:
        self.db: Optional[DatabaseConfig] = None
        self._session: Optional[Session] = None
        self.project_service: Optional[ProjectService] = None
        self.scene_service: Optional[SceneService] = None
        self.story_generator: Optional[StoryGenerator] = None
        self.character_service: Optional[CharacterService] = None
        self.location_service: Optional[LocationService] = None
        self.event_service: Optional[EventService] = None
        self.relationship_service: Optional[RelationshipService] = None
    
    def initialize(self) -> None:
        """Initialize database and services."""
        self.db = init_db(settings.get_database_url())
        self._session = self.db.SessionLocal()
        
        # Initialize repositories
        project_repo = SQLAlchemyProjectRepository(self._session)
        scene_repo = SQLAlchemySceneRepository(self._session)
        character_repo = SQLAlchemyCharacterRepository(self._session)
        location_repo = SQLAlchemyLocationRepository(self._session)
        event_repo = SQLAlchemyEventRepository(self._session)
        relationship_repo = SQLAlchemyRelationshipRepository(self._session)
        
        # Initialize services
        self.project_service = ProjectService(project_repo)
        self.scene_service = SceneService(scene_repo)
        self.story_generator = StoryGenerator(self._session)
        self.character_service = CharacterService(character_repo)
        self.location_service = LocationService(location_repo)
        self.event_service = EventService(event_repo)
        self.relationship_service = RelationshipService(relationship_repo)
        
        # Initialize LLM team from preferences
        self._initialize_llm_team()
    
    def _initialize_llm_team(self) -> None:
        """Initialize LLM team from preferences."""
        try:
            prefs = get_preferences()
            if prefs.llm_team and prefs.llm_team.get("members"):
                initialize_team_from_config(prefs.llm_team)
        except Exception as e:
            # If team initialization fails, just start with empty team
            print(f"Warning: Could not initialize LLM team: {e}")
    
    def commit(self) -> None:
        """Commit current transaction."""
        if self._session:
            self._session.commit()
    
    def rollback(self) -> None:
        """Rollback current transaction."""
        if self._session:
            self._session.rollback()
    
    def close(self) -> None:
        """Close database session."""
        if self._session:
            self._session.close()


# Global app context instance
_app_context: Optional[AppContext] = None


def get_app_context() -> AppContext:
    """Get the global app context."""
    global _app_context
    if _app_context is None:
        _app_context = AppContext()
        _app_context.initialize()
    return _app_context
