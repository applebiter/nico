"""Right panel widget with tabs for Inspector and AI tools."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
)

from nico.presentation.widgets.inspector import InspectorWidget
from nico.presentation.widgets.ai_panel import AIPanelWidget
from nico.domain.models import Project, Story, Chapter, Scene


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
        
        # Inspector tab (disabled by default, enabled only for scenes)
        self.inspector = InspectorWidget()
        self.inspector_tab_index = self.tabs.addTab(self.inspector, "🔍 Inspector")
        self.tabs.setTabEnabled(self.inspector_tab_index, False)
        
        # Set AI tab as default
        self.tabs.setCurrentIndex(self.ai_tab_index)
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
    def set_project_context(self, project: Project) -> None:
        """Update both panels with project context."""
        self.ai_panel.set_project_context(project)
        # Disable inspector for non-scene contexts
        self.tabs.setTabEnabled(self.inspector_tab_index, False)
        # Switch to AI tab
        self.tabs.setCurrentIndex(self.ai_tab_index)
        
    def set_story_context(self, story: Story) -> None:
        """Update both panels with story context."""
        self.ai_panel.set_story_context(story)
        # Disable inspector for non-scene contexts
        self.tabs.setTabEnabled(self.inspector_tab_index, False)
        # Switch to AI tab
        self.tabs.setCurrentIndex(self.ai_tab_index)
        
    def set_chapter_context(self, chapter: Chapter) -> None:
        """Update both panels with chapter context."""
        self.ai_panel.set_chapter_context(chapter)
        # Disable inspector for non-scene contexts
        self.tabs.setTabEnabled(self.inspector_tab_index, False)
        # Switch to AI tab
        self.tabs.setCurrentIndex(self.ai_tab_index)
        
    def set_scene_context(self, scene: Scene) -> None:
        """Update both panels with scene context."""
        self.ai_panel.set_scene_context(scene)
        self.inspector.load_scene(scene)
        # Enable inspector for scene context
        self.tabs.setTabEnabled(self.inspector_tab_index, True)
        # Keep AI tab active (user can switch to inspector if desired)
