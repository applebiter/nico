"""Continuous writing mode widget - seamless multi-scene writing."""
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLabel,
    QFrame,
    QScrollArea,
)
from PySide6.QtGui import QFont, QTextCursor

from nico.domain.models import Scene, Chapter
from nico.preferences import get_preferences


class SceneDivider(QFrame):
    """Visual divider between scenes in continuous mode."""
    
    def __init__(self, scene_title: str) -> None:
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        
        # Get theme-aware colors
        prefs = get_preferences()
        label_color = "#666" if prefs.theme == "dark" else "#999"
        bg_color = "#1e1e1e" if prefs.theme == "dark" else "#ffffff"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                margin: 40px 0px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scene indicator
        self.label = QLabel(f"• {scene_title} •")
        self.label.setStyleSheet(f"""
            QLabel {{
                color: {label_color};
                font-size: 11px;
                font-style: italic;
                background-color: {bg_color};
                padding: 4px 12px;
            }}
        """)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.label)
        self.setLayout(layout)


class ContinuousWritingWidget(QWidget):
    """Continuous writing mode showing multiple scenes seamlessly."""
    
    def __init__(self) -> None:
        super().__init__()
        self.current_chapter: Optional[Chapter] = None
        self.scenes: List[Scene] = []
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Get theme colors
        prefs = get_preferences()
        bg_color = "#1e1e1e" if prefs.theme == "dark" else "#ffffff"
        
        # Scroll area for continuous content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {bg_color};
            }}
        """)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(60, 40, 60, 40)
        self.content_layout.setSpacing(0)
        
        self.content_widget.setLayout(self.content_layout)
        self.content_widget.setStyleSheet(f"background-color: {bg_color};")
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        
    def load_chapter(self, chapter: Chapter) -> None:
        """Load all scenes from a chapter into continuous view."""
        self.current_chapter = chapter
        self.scenes = list(chapter.scenes)
        
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add each scene with dividers
        for i, scene in enumerate(self.scenes):
            # Add scene divider (except before first scene)
            if i > 0:
                divider = SceneDivider(scene.title)
                self.content_layout.addWidget(divider)
            
            # Add scene editor
            scene_text = self._create_scene_text_edit(scene)
            self.content_layout.addWidget(scene_text)
        
        self.content_layout.addStretch()
    
    def _create_scene_text_edit(self, scene: Scene) -> QTextEdit:
        """Create a text edit widget for a scene."""
        editor = QTextEdit()
        editor.setHtml(scene.content)
        
        # Get preferences for styling
        prefs = get_preferences()
        bg_color = "#1e1e1e" if prefs.theme == "dark" else "#ffffff"
        text_color = "#d4d4d4" if prefs.theme == "dark" else "#000000"
        
        # Set writing font with preferences
        font = QFont(prefs.editor_font, prefs.editor_font_size)
        editor.setFont(font)
        
        # Remove borders and make it look continuous
        editor.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                background-color: {bg_color};
                color: {text_color};
                padding: 0px;
            }}
        """)
        
        # Set frame to be flat
        editor.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Auto-adjust height based on content
        editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        editor.document().contentsChanged.connect(
            lambda: self._adjust_editor_height(editor)
        )
        
        # Store scene reference
        editor.setProperty("scene_id", scene.id)
        
        # Initial height adjustment
        self._adjust_editor_height(editor)
        
        return editor
    
    def _adjust_editor_height(self, editor: QTextEdit) -> None:
        """Adjust editor height to fit content."""
        doc_height = editor.document().size().height()
        editor.setMinimumHeight(int(doc_height) + 20)
        editor.setMaximumHeight(int(doc_height) + 20)
    
    def load_single_scene(self, scene: Scene) -> None:
        """Load a single scene (for backward compatibility)."""
        # Create a temporary chapter-like structure
        class TempChapter:
            def __init__(self, scene):
                self.scenes = [scene]
                self.title = "Single Scene"
        
        self.load_chapter(TempChapter(scene))
