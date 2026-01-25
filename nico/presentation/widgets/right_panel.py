"""Right panel widget with tabs for Inspector and AI tools."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
)

from nico.presentation.widgets.inspector import InspectorWidget
from nico.presentation.widgets.ai_panel import AIPanelWidget
from nico.domain.models import Project, Story, Chapter, Scene, Character
from nico.application.context import AppContext


class RightPanelWidget(QWidget):
    """Right panel with tabbed interface for Inspector and AI tools."""
    
    def __init__(self, app_context: AppContext) -> None:
        super().__init__()
        self.app_context = app_context
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Inspector tab (default, appears first)
        self.inspector = InspectorWidget(self.app_context)
        self.inspector_tab_index = self.tabs.addTab(self.inspector, "🔍 Inspector")
        
        # AI panel tab (appears second, on the right)
        self.ai_panel = AIPanelWidget()
        self.ai_tab_index = self.tabs.addTab(self.ai_panel, "🤖 AI Assistant")
        
        # Set Inspector tab as default
        self.tabs.setCurrentIndex(self.inspector_tab_index)
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
    def set_project_context(self, project: Project) -> None:
        """Update both panels with project context."""
        self.ai_panel.set_project_context(project)
        self.inspector.load_project(project)
        # Switch to Inspector tab
        self.tabs.setCurrentIndex(self.inspector_tab_index)
        
    def set_story_context(self, story: Story) -> None:
        """Update both panels with story context."""
        self.ai_panel.set_story_context(story)
        self.inspector.load_story(story)
        # Switch to Inspector tab
        self.tabs.setCurrentIndex(self.inspector_tab_index)
        
    def set_chapter_context(self, chapter: Chapter) -> None:
        """Update both panels with chapter context."""
        self.ai_panel.set_chapter_context(chapter)
        self.inspector.load_chapter(chapter)
        # Switch to Inspector tab
        self.tabs.setCurrentIndex(self.inspector_tab_index)
    
    def set_character_context(self, character: Character) -> None:
        """Update both panels with character context."""
        # AI panel doesn't have character context yet, so just update inspector
        self.inspector.load_character(character)
        # Switch to Inspector tab
        self.tabs.setCurrentIndex(self.inspector_tab_index)
        
    def set_scene_context(self, scene: Scene) -> None:
        """Update both panels with scene context."""
        self.ai_panel.set_scene_context(scene)
        self.inspector.load_scene(scene)
        # Switch to Inspector tab
        self.tabs.setCurrentIndex(self.inspector_tab_index)
