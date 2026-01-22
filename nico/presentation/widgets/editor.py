"""Editor widget - main writing surface."""
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
)

from nico.domain.models import Scene, Project, Story, Chapter, Character, Location, Event
from nico.presentation.widgets.project_overview import ProjectOverview
from nico.presentation.widgets.story_overview import StoryOverview
from nico.presentation.widgets.stories_overview import StoriesOverview
from nico.presentation.widgets.chapter_overview import ChapterOverview
from nico.presentation.widgets.scene_editor import SceneEditor
from nico.presentation.widgets.character_profile import CharacterProfileWidget
from nico.presentation.widgets.characters_overview import CharactersOverview


class EditorWidget(QWidget):
    """Center panel: Displays different content based on selection type."""
    
    # Forward signals from child widgets for navigation
    story_selected = Signal(int)
    chapter_selected = Signal(int)
    scene_selected = Signal(int)
    character_selected = Signal(int)  # Added for characters overview navigation
    
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget to switch between different views
        self.stack = QStackedWidget()
        
        # Create views
        self.project_overview = ProjectOverview()
        self.stories_overview = StoriesOverview()
        self.story_overview = StoryOverview()
        self.chapter_overview = ChapterOverview()
        self.scene_editor = SceneEditor()
        self.character_profile = CharacterProfileWidget()
        self.characters_overview = CharactersOverview()
        
        # TODO: Add location and event viewers when needed
        
        # Connect navigation signals
        self.project_overview.story_selected.connect(self.story_selected.emit)
        self.stories_overview.story_selected.connect(self.story_selected.emit)
        self.story_overview.chapter_selected.connect(self.chapter_selected.emit)
        self.chapter_overview.scene_selected.connect(self.scene_selected.emit)
        self.chapter_overview.continuous_writing_requested.connect(self._on_continuous_writing_requested)
        self.characters_overview.character_selected.connect(self.character_selected.emit)
        
        # Note: character_updated and story_updated signals will be connected in main_window
        
        # Add to stack
        self.stack.addWidget(self.project_overview)
        self.stack.addWidget(self.stories_overview)
        self.stack.addWidget(self.story_overview)
        self.stack.addWidget(self.chapter_overview)
        self.stack.addWidget(self.scene_editor)
        self.stack.addWidget(self.character_profile)
        self.stack.addWidget(self.characters_overview)
        
        layout.addWidget(self.stack)
        self.setLayout(layout)
        
    def show_project(self, project: Project) -> None:
        """Display project overview."""
        self.project_overview.load_project(project)
        self.stack.setCurrentWidget(self.project_overview)
        
    def show_story(self, story: Story) -> None:
        """Display story overview."""
        self.story_overview.load_story(story)
        self.stack.setCurrentWidget(self.story_overview)
        
    def show_chapter(self, chapter: Chapter) -> None:
        """Display chapter overview."""
        self.chapter_overview.load_chapter(chapter)
        self.stack.setCurrentWidget(self.chapter_overview)
        
    def show_scene(self, scene: Scene) -> None:
        """Display scene editor."""
        self.scene_editor.load_scene(scene)
        self.stack.setCurrentWidget(self.scene_editor)
    
    def show_chapter_continuous(self, chapter: Chapter) -> None:
        """Display chapter in continuous writing mode."""
        self.scene_editor.load_chapter_continuous(chapter)
        self.stack.setCurrentWidget(self.scene_editor)
    
    def _on_continuous_writing_requested(self, chapter_id: int) -> None:
        """Handle request to switch to continuous writing mode."""
        # Need to get the chapter object - signal up to main window
        # For now, use the current chapter if available
        if hasattr(self.chapter_overview, 'current_chapter') and self.chapter_overview.current_chapter:
            self.show_chapter_continuous(self.chapter_overview.current_chapter)
    
    def show_character(self, character_id: int) -> None:
        """Display character profile."""
        self.character_profile.load_character(character_id)
        self.stack.setCurrentWidget(self.character_profile)
    
    def show_characters_overview(self, project: Project) -> None:
        """Display characters overview for a project."""
        self.characters_overview.load_project(project)
        self.stack.setCurrentWidget(self.characters_overview)
    
    def show_stories_overview(self, project: Project) -> None:
        """Display stories overview for a project."""
        self.stories_overview.load_project(project)
        self.stack.setCurrentWidget(self.stories_overview)
    
    def show_location(self, location_id: int) -> None:
        """Display location profile."""
        # TODO: Implement location viewer
        pass
    
    def show_event(self, event_id: int) -> None:
        """Display event details."""
        # TODO: Implement event viewer
        pass
