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


class RightPanelWidget(QWidget):
    """Right panel with tabbed interface for Inspector and AI tools."""
    
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # AI panel tab (now first/default)
        self.ai_panel = AIPanelWidget()
        self.ai_tab_index = self.tabs.addTab(self.ai_panel, "🤖 AI Assistant")
        
        # Inspector tab (now always enabled)
        self.inspector = InspectorWidget()
        self.inspector_tab_index = self.tabs.addTab(self.inspector, "🔍 Inspector")
        
        # Set AI tab as default
        self.tabs.setCurrentIndex(self.ai_tab_index)
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
    def set_project_context(self, project: Project) -> None:
        """Update both panels with project context."""
        self.ai_panel.set_project_context(project)
        self.inspector.load_project(project)
        # Keep AI tab active
        self.tabs.setCurrentIndex(self.ai_tab_index)
        
    def set_story_context(self, story: Story) -> None:
        """Update both panels with story context."""
        self.ai_panel.set_story_context(story)
        self.inspector.load_story(story)
        # Keep AI tab active
        self.tabs.setCurrentIndex(self.ai_tab_index)
        
    def set_chapter_context(self, chapter: Chapter) -> None:
        """Update both panels with chapter context."""
        self.ai_panel.set_chapter_context(chapter)
        self.inspector.load_chapter(chapter)
        # Keep AI tab active
        self.tabs.setCurrentIndex(self.ai_tab_index)
    
    def set_character_context(self, character: Character) -> None:
        """Update both panels with character context."""
        # AI panel doesn't have character context yet, so just update inspector
        self.inspector.load_character(character)
        # Keep AI tab active
        self.tabs.setCurrentIndex(self.ai_tab_index)
        
    def set_scene_context(self, scene: Scene) -> None:
        """Update both panels with scene context."""
        self.ai_panel.set_scene_context(scene)
        self.inspector.load_scene(scene)
        # Keep AI tab active (user can switch to inspector if desired)
