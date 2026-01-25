"""Inspector widget - properties and metadata panel."""
from typing import Optional
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QScrollArea,
    QPushButton,
    QSlider,
    QListWidget,
    QListWidgetItem,
    QInputDialog,
    QMessageBox,
    QStackedWidget,
)

from nico.domain.models import Scene, Project, Story, Chapter, Character


class TraitItem(QWidget):
    """Widget for a single character trait with slider."""
    
    removed = Signal(str)  # trait_name
    value_changed = Signal(str, int)  # trait_name, value
    
    def __init__(self, trait_name: str, value: int = 5, parent=None):
        super().__init__(parent)
        self.trait_name = trait_name
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 2, 0, 2)
        
        # Trait name label
        self.label = QLabel(trait_name)
        self.label.setMinimumWidth(80)
        layout.addWidget(self.label)
        
        # Slider (1-10)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(10)
        self.slider.setValue(value)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)
        
        # Value label
        self.value_label = QLabel(str(value))
        self.value_label.setMinimumWidth(20)
        layout.addWidget(self.value_label)
        
        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setMaximumWidth(25)
        remove_btn.clicked.connect(lambda: self.removed.emit(self.trait_name))
        layout.addWidget(remove_btn)
        
        self.setLayout(layout)
    
    def _on_value_changed(self, value: int):
        """Update value label and emit signal."""
        self.value_label.setText(str(value))
        self.value_changed.emit(self.trait_name, value)
    
    def get_value(self) -> int:
        """Get current slider value."""
        return self.slider.value()


class InspectorWidget(QWidget):
    """Right panel: Properties and metadata for selected item."""
    
    def __init__(self) -> None:
        super().__init__()
        self.current_context = None
        self.current_context_type = None
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        self.title_label = QLabel("🔍 Inspector")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(self.title_label)
        
        # Stacked widget for different contexts
        self.stack = QStackedWidget()
        
        # Create pages for each context type
        self.empty_page = self._create_empty_page()
        self.project_page = self._create_project_page()
        self.story_page = self._create_story_page()
        self.chapter_page = self._create_chapter_page()
        self.character_page = self._create_character_page()
        self.scene_page = self._create_scene_page()
        
        self.stack.addWidget(self.empty_page)
        self.stack.addWidget(self.project_page)
        self.stack.addWidget(self.story_page)
        self.stack.addWidget(self.chapter_page)
        self.stack.addWidget(self.character_page)
        self.stack.addWidget(self.scene_page)
        
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)
    
    def _create_empty_page(self) -> QWidget:
        """Create empty state page."""
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Select an item to view its properties")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #666;")
        layout.addWidget(label)
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_project_page(self) -> QWidget:
        """Create project inspector page."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Notes group
        notes_group = QGroupBox("Project Notes")
        notes_layout = QVBoxLayout()
        self.project_notes_text = QTextEdit()
        self.project_notes_text.setPlaceholderText("Project notes, ideas, research...")
        self.project_notes_text.setMinimumHeight(150)
        notes_layout.addWidget(self.project_notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout()
        self.project_stories_label = QLabel("0")
        stats_layout.addRow("Stories:", self.project_stories_label)
        self.project_chapters_label = QLabel("0")
        stats_layout.addRow("Chapters:", self.project_chapters_label)
        self.project_scenes_label = QLabel("0")
        stats_layout.addRow("Scenes:", self.project_scenes_label)
        self.project_words_label = QLabel("0")
        stats_layout.addRow("Total Words:", self.project_words_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)
        return widget
    
    def _create_story_page(self) -> QWidget:
        """Create story inspector page."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Summary group
        summary_group = QGroupBox("Story Summary")
        summary_layout = QVBoxLayout()
        self.story_summary_text = QTextEdit()
        self.story_summary_text.setPlaceholderText("Story synopsis...")
        self.story_summary_text.setMinimumHeight(100)
        summary_layout.addWidget(self.story_summary_text)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Notes group
        notes_group = QGroupBox("Story Notes")
        notes_layout = QVBoxLayout()
        self.story_notes_text = QTextEdit()
        self.story_notes_text.setPlaceholderText("Research notes, plot points...")
        self.story_notes_text.setMinimumHeight(150)
        notes_layout.addWidget(self.story_notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout()
        self.story_chapters_label = QLabel("0")
        stats_layout.addRow("Chapters:", self.story_chapters_label)
        self.story_scenes_label = QLabel("0")
        stats_layout.addRow("Scenes:", self.story_scenes_label)
        self.story_words_label = QLabel("0")
        stats_layout.addRow("Word Count:", self.story_words_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)
        return widget
    
    def _create_chapter_page(self) -> QWidget:
        """Create chapter inspector page."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Summary group
        summary_group = QGroupBox("Chapter Summary")
        summary_layout = QVBoxLayout()
        self.chapter_summary_text = QTextEdit()
        self.chapter_summary_text.setPlaceholderText("Chapter summary...")
        self.chapter_summary_text.setMinimumHeight(100)
        summary_layout.addWidget(self.chapter_summary_text)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Notes group
        notes_group = QGroupBox("Chapter Notes")
        notes_layout = QVBoxLayout()
        self.chapter_notes_text = QTextEdit()
        self.chapter_notes_text.setPlaceholderText("Plot points, reminders...")
        self.chapter_notes_text.setMinimumHeight(150)
        notes_layout.addWidget(self.chapter_notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout()
        self.chapter_scenes_label = QLabel("0")
        stats_layout.addRow("Scenes:", self.chapter_scenes_label)
        self.chapter_words_label = QLabel("0")
        stats_layout.addRow("Word Count:", self.chapter_words_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)
        return widget
    
    def _create_character_page(self) -> QWidget:
        """Create character inspector page."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Traits group
        traits_group = QGroupBox("Character Traits")
        traits_layout = QVBoxLayout()
        
        # Add trait button
        add_trait_btn = QPushButton("➕ Add Trait")
        add_trait_btn.clicked.connect(self._on_add_trait)
        traits_layout.addWidget(add_trait_btn)
        
        # Traits container
        self.traits_container = QWidget()
        self.traits_layout = QVBoxLayout()
        self.traits_layout.setContentsMargins(0, 5, 0, 0)
        self.traits_container.setLayout(self.traits_layout)
        traits_layout.addWidget(self.traits_container)
        
        traits_group.setLayout(traits_layout)
        layout.addWidget(traits_group)
        
        # Relationships group
        relationships_group = QGroupBox("Relationships")
        relationships_layout = QVBoxLayout()
        
        self.relationships_list = QListWidget()
        self.relationships_list.setMaximumHeight(150)
        relationships_layout.addWidget(self.relationships_list)
        
        add_relationship_btn = QPushButton("➕ Add Relationship")
        add_relationship_btn.clicked.connect(self._on_add_relationship)
        relationships_layout.addWidget(add_relationship_btn)
        
        relationships_group.setLayout(relationships_layout)
        layout.addWidget(relationships_group)
        
        # Notes group
        notes_group = QGroupBox("Character Notes")
        notes_layout = QVBoxLayout()
        self.character_notes_text = QTextEdit()
        self.character_notes_text.setPlaceholderText("Character development notes...")
        self.character_notes_text.setMinimumHeight(100)
        notes_layout.addWidget(self.character_notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        layout.addStretch()
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)
        return widget
    
    def _create_scene_page(self) -> QWidget:
        """Create scene inspector page."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scene metadata group
        metadata_group = QGroupBox("Scene Metadata")
        metadata_layout = QFormLayout()
        
        self.scene_title_field = QLineEdit()
        self.scene_title_field.setPlaceholderText("Scene title...")
        metadata_layout.addRow("Title:", self.scene_title_field)
        
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
        layout.addWidget(metadata_group)
        
        # Scene summary group
        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout()
        
        self.scene_summary_text = QTextEdit()
        self.scene_summary_text.setPlaceholderText("Brief summary of this scene...")
        self.scene_summary_text.setMaximumHeight(100)
        
        summary_layout.addWidget(self.scene_summary_text)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Notes group
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        
        self.scene_notes_text = QTextEdit()
        self.scene_notes_text.setPlaceholderText("Research notes, ideas, reminders...")
        self.scene_notes_text.setMaximumHeight(150)
        
        notes_layout.addWidget(self.scene_notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
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
        layout.addWidget(stats_group)
        
        layout.addStretch()
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)
        return widget
    
    def load_project(self, project: Project) -> None:
        """Load project data into the inspector."""
        self.current_context = project
        self.current_context_type = "project"
        self.title_label.setText("🔍 Inspector - Project")
        self.stack.setCurrentWidget(self.project_page)
        
        # Load project notes from meta
        if project.meta:
            self.project_notes_text.setPlainText(project.meta.get('notes', ''))
        else:
            self.project_notes_text.clear()
        
        # TODO: Load statistics (requires queries)
        self.project_stories_label.setText("0")
        self.project_chapters_label.setText("0")
        self.project_scenes_label.setText("0")
        self.project_words_label.setText("0")
    
    def load_story(self, story: Story) -> None:
        """Load story data into the inspector."""
        self.current_context = story
        self.current_context_type = "story"
        self.title_label.setText("🔍 Inspector - Story")
        self.stack.setCurrentWidget(self.story_page)
        
        # Load story data from meta
        if story.meta:
            self.story_summary_text.setPlainText(story.meta.get('summary', ''))
            self.story_notes_text.setPlainText(story.meta.get('notes', ''))
        else:
            self.story_summary_text.clear()
            self.story_notes_text.clear()
        
        # TODO: Load statistics
        self.story_chapters_label.setText("0")
        self.story_scenes_label.setText("0")
        self.story_words_label.setText("0")
    
    def load_chapter(self, chapter: Chapter) -> None:
        """Load chapter data into the inspector."""
        self.current_context = chapter
        self.current_context_type = "chapter"
        self.title_label.setText("🔍 Inspector - Chapter")
        self.stack.setCurrentWidget(self.chapter_page)
        
        # Load chapter data from meta
        if chapter.meta:
            self.chapter_summary_text.setPlainText(chapter.meta.get('summary', ''))
            self.chapter_notes_text.setPlainText(chapter.meta.get('notes', ''))
        else:
            self.chapter_summary_text.clear()
            self.chapter_notes_text.clear()
        
        # TODO: Load statistics
        self.chapter_scenes_label.setText("0")
        self.chapter_words_label.setText("0")
    
    def load_character(self, character: Character) -> None:
        """Load character data into the inspector."""
        self.current_context = character
        self.current_context_type = "character"
        self.title_label.setText(f"🔍 Inspector - Character")
        self.stack.setCurrentWidget(self.character_page)
        
        # Clear existing traits
        self._clear_traits()
        
        # Load traits from meta
        if character.meta and 'traits' in character.meta:
            for trait_name, value in character.meta['traits'].items():
                self._add_trait_widget(trait_name, value)
        
        # Load relationships
        self.relationships_list.clear()
        if character.meta and 'relationships' in character.meta:
            for rel in character.meta['relationships']:
                self.relationships_list.addItem(rel)
        
        # Load notes
        if character.meta:
            self.character_notes_text.setPlainText(character.meta.get('notes', ''))
        else:
            self.character_notes_text.clear()
    
    def load_scene(self, scene: Scene) -> None:
        """Load scene data into the inspector."""
        self.current_context = scene
        self.current_context_type = "scene"
        self.title_label.setText("🔍 Inspector - Scene")
        self.stack.setCurrentWidget(self.scene_page)
        
        # Update metadata fields
        self.scene_title_field.setText(scene.title or "")
        self.beat_field.setText(scene.beat or "")
        
        # Extract POV and setting from meta JSONB
        if scene.meta:
            self.pov_field.setText(scene.meta.get('pov', ''))
            self.setting_field.setText(scene.meta.get('setting', ''))
            self.scene_summary_text.setPlainText(scene.meta.get('summary', ''))
            self.scene_notes_text.setPlainText(scene.meta.get('notes', ''))
        else:
            self.pov_field.setText("")
            self.setting_field.setText("")
            self.scene_summary_text.setPlainText("")
            self.scene_notes_text.setPlainText("")
        
        # Update statistics
        self.word_count_label.setText(f"{scene.word_count:,}")
        
        # Format dates
        if scene.created_at:
            self.created_label.setText(scene.created_at.strftime("%b %d, %Y"))
        if scene.updated_at:
            self.modified_label.setText(scene.updated_at.strftime("%b %d, %Y %H:%M"))
    
    def _clear_traits(self):
        """Remove all trait widgets."""
        while self.traits_layout.count():
            item = self.traits_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _add_trait_widget(self, trait_name: str, value: int = 5):
        """Add a trait widget to the container."""
        trait_widget = TraitItem(trait_name, value)
        trait_widget.removed.connect(self._on_remove_trait)
        trait_widget.value_changed.connect(self._on_trait_value_changed)
        self.traits_layout.addWidget(trait_widget)
    
    def _on_add_trait(self):
        """Add a new trait."""
        if not isinstance(self.current_context, Character):
            return
        
        trait_name, ok = QInputDialog.getText(
            self,
            "Add Trait",
            "Enter trait name (e.g., 'dependable', 'moody'):"
        )
        
        if ok and trait_name.strip():
            trait_name = trait_name.strip().lower()
            
            # Check if trait already exists
            if self.current_context.meta and 'traits' in self.current_context.meta:
                if trait_name in self.current_context.meta['traits']:
                    QMessageBox.warning(self, "Duplicate Trait", "This trait already exists.")
                    return
            
            # Add trait widget
            self._add_trait_widget(trait_name, 5)
            
            # Save to character meta
            if not self.current_context.meta:
                self.current_context.meta = {}
            if 'traits' not in self.current_context.meta:
                self.current_context.meta['traits'] = {}
            self.current_context.meta['traits'][trait_name] = 5
            
            # TODO: Save to database
    
    def _on_remove_trait(self, trait_name: str):
        """Remove a trait."""
        if not isinstance(self.current_context, Character):
            return
        
        # Remove from meta
        if self.current_context.meta and 'traits' in self.current_context.meta:
            self.current_context.meta['traits'].pop(trait_name, None)
        
        # Remove widget
        for i in range(self.traits_layout.count()):
            widget = self.traits_layout.itemAt(i).widget()
            if isinstance(widget, TraitItem) and widget.trait_name == trait_name:
                widget.deleteLater()
                break
        
        # TODO: Save to database
    
    def _on_trait_value_changed(self, trait_name: str, value: int):
        """Handle trait value change."""
        if not isinstance(self.current_context, Character):
            return
        
        # Update meta
        if not self.current_context.meta:
            self.current_context.meta = {}
        if 'traits' not in self.current_context.meta:
            self.current_context.meta['traits'] = {}
        self.current_context.meta['traits'][trait_name] = value
        
        # TODO: Save to database
    
    def _on_add_relationship(self):
        """Add a new relationship."""
        if not isinstance(self.current_context, Character):
            return
        
        relationship, ok = QInputDialog.getText(
            self,
            "Add Relationship",
            "Describe relationship (e.g., 'Sister of John', 'Enemy of the King'):"
        )
        
        if ok and relationship.strip():
            self.relationships_list.addItem(relationship.strip())
            
            # Save to character meta
            if not self.current_context.meta:
                self.current_context.meta = {}
            if 'relationships' not in self.current_context.meta:
                self.current_context.meta['relationships'] = []
            self.current_context.meta['relationships'].append(relationship.strip())
            
            # TODO: Save to database
    
    def clear(self) -> None:
        """Clear all inspector fields and show empty state."""
        self.current_context = None
        self.current_context_type = None
        self.title_label.setText("🔍 Inspector")
        self.stack.setCurrentWidget(self.empty_page)
