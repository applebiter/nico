"""Scene editor widget - rich text editor for scene content."""
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLabel,
    QToolBar,
    QComboBox,
    QPushButton,
    QStackedWidget,
)
from PySide6.QtGui import QFont

from nico.domain.models import Scene
from nico.presentation.widgets.continuous_writing import ContinuousWritingWidget


class SceneEditor(QWidget):
    """Rich text editor for scene content with optional continuous mode."""
    
    # Signal emitted when switching to continuous mode for a chapter
    continuous_mode_requested = Signal(int)  # chapter_id
    
    def __init__(self) -> None:
        super().__init__()
        self.current_scene: Optional[Scene] = None
        self.current_chapter_id: Optional[int] = None
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Mode selector at the top
        mode_header = QHBoxLayout()
        mode_label = QLabel("View Mode:")
        mode_label.setStyleSheet("font-weight: bold;")
        mode_header.addWidget(mode_label)
        
        self.scene_mode_btn = QPushButton("📄 Scene")
        self.scene_mode_btn.setCheckable(True)
        self.scene_mode_btn.setChecked(True)
        self.scene_mode_btn.clicked.connect(self._switch_to_scene_mode)
        mode_header.addWidget(self.scene_mode_btn)
        
        self.continuous_mode_btn = QPushButton("📖 Continuous Writing")
        self.continuous_mode_btn.setCheckable(True)
        self.continuous_mode_btn.clicked.connect(self._switch_to_continuous_mode)
        mode_header.addWidget(self.continuous_mode_btn)
        
        mode_header.addStretch()
        layout.addLayout(mode_header)
        
        # Stacked widget for different modes
        self.mode_stack = QStackedWidget()
        
        # Scene mode (individual scene editing)
        scene_mode_widget = QWidget()
        scene_layout = QVBoxLayout()
        scene_layout.setContentsMargins(0, 5, 0, 0)
        
        # Header with scene info
        header = QHBoxLayout()
        self.scene_title = QLabel("No scene selected")
        self.scene_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(self.scene_title)
        
        header.addStretch()
        
        self.word_count = QLabel("0 words")
        self.word_count.setStyleSheet("color: #666;")
        header.addWidget(self.word_count)
        
        scene_layout.addLayout(header)
        
        # Formatting toolbar (placeholder)
        toolbar = QToolBar()
        toolbar.addAction("B", self._on_bold)
        toolbar.addAction("I", self._on_italic)
        toolbar.addAction("U", self._on_underline)
        toolbar.addSeparator()
        
        # Font size combo
        font_size = QComboBox()
        font_size.addItems(["10", "12", "14", "16", "18", "20", "24"])
        font_size.setCurrentText("14")
        toolbar.addWidget(font_size)
        
        scene_layout.addWidget(toolbar)
        
        # Text editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Select a scene to start writing...")
        
        # Set a nice writing font
        font = QFont("Georgia", 14)
        self.editor.setFont(font)
        
        scene_layout.addWidget(self.editor)
        
        # Footer with scene metadata
        self.footer = QHBoxLayout()
        self.beat_label = QLabel("")
        self.pov_label = QLabel("")
        self.setting_label = QLabel("")
        
        self.footer.addWidget(self.beat_label)
        self.footer.addStretch()
        self.footer.addWidget(self.pov_label)
        self.footer.addWidget(self.setting_label)
        
        scene_layout.addLayout(self.footer)
        scene_mode_widget.setLayout(scene_layout)
        
        # Continuous mode
        self.continuous_widget = ContinuousWritingWidget()
        
        # Add both modes to stack
        self.mode_stack.addWidget(scene_mode_widget)
        self.mode_stack.addWidget(self.continuous_widget)
        
        layout.addWidget(self.mode_stack)
        self.setLayout(layout)
    
    def load_scene(self, scene: Scene) -> None:
        """Load a scene into the editor."""
        self.current_scene = scene
        # Store chapter_id if available (needed for continuous mode)
        self.current_chapter_id = scene.chapter_id if hasattr(scene, 'chapter_id') else None
        
        # Switch to scene mode by default
        self._switch_to_scene_mode()
        
        # Update header
        self.scene_title.setText(f"✍️ {scene.title}")
        self.word_count.setText(f"{scene.word_count:,} words")
        
        # Load content
        self.editor.setHtml(scene.content)
        
        # Update footer
        self.beat_label.setText(f"Beat: {scene.beat}" if scene.beat else "")
        
        if scene.meta:
            pov = scene.meta.get('pov', '')
            setting = scene.meta.get('setting', '')
            self.pov_label.setText(f"POV: {pov}" if pov else "")
            self.setting_label.setText(f"Setting: {setting}" if setting else "")
        else:
            self.pov_label.setText("")
            self.setting_label.setText("")
    
    def load_chapter_continuous(self, chapter) -> None:
        """Load entire chapter in continuous writing mode."""
        self.current_chapter_id = chapter.id
        self._switch_to_continuous_mode()
        self.continuous_widget.load_chapter(chapter)
    
    def _switch_to_scene_mode(self) -> None:
        """Switch to single scene editing mode."""
        self.scene_mode_btn.setChecked(True)
        self.continuous_mode_btn.setChecked(False)
        self.mode_stack.setCurrentIndex(0)
    
    def _switch_to_continuous_mode(self) -> None:
        """Switch to continuous writing mode."""
        self.continuous_mode_btn.setChecked(True)
        self.scene_mode_btn.setChecked(False)
        self.mode_stack.setCurrentIndex(1)
        
        # Load current scene in continuous mode
        if self.current_scene:
            self.continuous_widget.load_single_scene(self.current_scene)
        else:
            self.pov_label.setText("")
            self.setting_label.setText("")
        
    # Formatting action handlers (placeholders)
    def _on_bold(self) -> None:
        """Toggle bold formatting."""
        pass
        
    def _on_italic(self) -> None:
        """Toggle italic formatting."""
        pass
        
    def _on_underline(self) -> None:
        """Toggle underline formatting."""
        pass
