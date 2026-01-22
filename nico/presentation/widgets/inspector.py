"""Inspector widget - properties and metadata panel."""
from typing import Optional
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QScrollArea,
)

from nico.domain.models import Scene


class InspectorWidget(QWidget):
    """Right panel: Properties and metadata for selected item."""
    
    def __init__(self) -> None:
        super().__init__()
        self.current_scene: Optional[Scene] = None
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("🔍 Inspector")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scene metadata group
        metadata_group = QGroupBox("Scene Metadata")
        metadata_layout = QFormLayout()
        
        self.title_field = QLineEdit()
        self.title_field.setPlaceholderText("Scene title...")
        metadata_layout.addRow("Title:", self.title_field)
        
        self.beat_field = QLineEdit()
        self.beat_field.setPlaceholderText("Story beat...")
        metadata_layout.addRow("Beat:", self.beat_field)
        
        self.pov_field = QLineEdit()
        self.pov_field.setPlaceholderText("POV character...")
        metadata_layout.addRow("POV:", self.pov_field)
        
        self.setting_field = QLineEdit()
        self.setting_field.setPlaceholderText("Setting/location...")
        metadata_layout.addRow("Setting:", self.setting_field)
        
        metadata_group.setLayout(metadata_layout)
        content_layout.addWidget(metadata_group)
        
        # Scene summary group
        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setPlaceholderText("Brief summary of this scene...")
        self.summary_text.setMaximumHeight(100)
        
        summary_layout.addWidget(self.summary_text)
        summary_group.setLayout(summary_layout)
        content_layout.addWidget(summary_group)
        
        # Notes group
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Research notes, ideas, reminders...")
        self.notes_text.setMaximumHeight(150)
        
        notes_layout.addWidget(self.notes_text)
        notes_group.setLayout(notes_layout)
        content_layout.addWidget(notes_group)
        
        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout()
        
        self.word_count_label = QLabel("0")
        stats_layout.addRow("Word Count:", self.word_count_label)
        
        self.target_label = QLabel("-")
        stats_layout.addRow("Target:", self.target_label)
        
        self.created_label = QLabel("-")
        stats_layout.addRow("Created:", self.created_label)
        
        self.modified_label = QLabel("-")
        stats_layout.addRow("Modified:", self.modified_label)
        
        stats_group.setLayout(stats_layout)
        content_layout.addWidget(stats_group)
        
        # AI Settings group
        ai_group = QGroupBox("AI Settings")
        ai_layout = QFormLayout()
        
        ai_layout.addRow("Exclude from AI:", QLabel("No"))
        
        ai_group.setLayout(ai_layout)
        content_layout.addWidget(ai_group)
        
        content_layout.addStretch()
        
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def load_scene(self, scene: Scene) -> None:
        """Load scene data into the inspector."""
        self.current_scene = scene
        
        # Update metadata fields
        self.title_field.setText(scene.title or "")
        self.beat_field.setText(scene.beat or "")
        
        # Extract POV and setting from meta JSONB
        if scene.meta:
            self.pov_field.setText(scene.meta.get('pov', ''))
            self.setting_field.setText(scene.meta.get('setting', ''))
            self.summary_text.setPlainText(scene.meta.get('summary', ''))
            self.notes_text.setPlainText(scene.meta.get('notes', ''))
        else:
            self.pov_field.setText("")
            self.setting_field.setText("")
            self.summary_text.setPlainText("")
            self.notes_text.setPlainText("")
        
        # Update statistics
        self.word_count_label.setText(f"{scene.word_count:,}")
        
        # Format dates
        if scene.created_at:
            self.created_label.setText(scene.created_at.strftime("%b %d, %Y"))
        if scene.updated_at:
            self.modified_label.setText(scene.updated_at.strftime("%b %d, %Y %H:%M"))
    
    def clear(self) -> None:
        """Clear all inspector fields."""
        self.current_scene = None
        self.title_field.clear()
        self.beat_field.clear()
        self.pov_field.clear()
        self.setting_field.clear()
        self.summary_text.clear()
        self.notes_text.clear()
        self.word_count_label.setText("0")
        self.target_label.setText("-")
        self.created_label.setText("-")
        self.modified_label.setText("-")
