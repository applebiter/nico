"""Inspector widget - properties and metadata panel."""
from typing import Optional
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QSize
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
    QMenu,
)

from nico.domain.models import (
    Scene, Project, Story, Chapter, Character,
    Relationship, CharacterMotifRelationship, SymbolicMotif, Media,
)
from nico.application.context import AppContext
from nico.presentation.widgets.relationship_dialog import RelationshipDialog
from nico.presentation.widgets.media_picker_dialog import MediaPickerDialog


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
    
    def __init__(self, app_context: AppContext) -> None:
        super().__init__()
        self.app_context = app_context
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
        self.project_notes_text.setAcceptRichText(False)
        self.project_notes_text.setPlaceholderText("Project notes, ideas, research...")
        self.project_notes_text.setMinimumHeight(150)
        notes_layout.addWidget(self.project_notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Media group
        project_media_group = QGroupBox("Media")
        project_media_layout = QVBoxLayout()
        
        self.project_media_list = QListWidget()
        self.project_media_list.setMaximumHeight(120)
        project_media_layout.addWidget(self.project_media_list)
        
        project_media_btn_layout = QHBoxLayout()
        project_attach_media_btn = QPushButton("📎 Attach")
        project_attach_media_btn.clicked.connect(lambda: self._on_attach_media_generic('project'))
        project_media_btn_layout.addWidget(project_attach_media_btn)
        
        project_detach_media_btn = QPushButton("✂️ Detach")
        project_detach_media_btn.clicked.connect(lambda: self._on_detach_media_generic('project'))
        project_media_btn_layout.addWidget(project_detach_media_btn)
        
        project_media_layout.addLayout(project_media_btn_layout)
        project_media_group.setLayout(project_media_layout)
        layout.addWidget(project_media_group)
        
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
        self.story_summary_text.setAcceptRichText(False)
        self.story_summary_text.setPlaceholderText("Story synopsis...")
        self.story_summary_text.setMinimumHeight(100)
        summary_layout.addWidget(self.story_summary_text)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Notes group
        notes_group = QGroupBox("Story Notes")
        notes_layout = QVBoxLayout()
        self.story_notes_text = QTextEdit()
        self.story_notes_text.setAcceptRichText(False)
        self.story_notes_text.setPlaceholderText("Research notes, plot points...")
        self.story_notes_text.setMinimumHeight(150)
        notes_layout.addWidget(self.story_notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Media group
        story_media_group = QGroupBox("Media")
        story_media_layout = QVBoxLayout()
        
        self.story_media_list = QListWidget()
        self.story_media_list.setMaximumHeight(120)
        story_media_layout.addWidget(self.story_media_list)
        
        story_media_btn_layout = QHBoxLayout()
        story_attach_media_btn = QPushButton("📎 Attach")
        story_attach_media_btn.clicked.connect(lambda: self._on_attach_media_generic('story'))
        story_media_btn_layout.addWidget(story_attach_media_btn)
        
        story_detach_media_btn = QPushButton("✂️ Detach")
        story_detach_media_btn.clicked.connect(lambda: self._on_detach_media_generic('story'))
        story_media_btn_layout.addWidget(story_detach_media_btn)
        
        story_media_layout.addLayout(story_media_btn_layout)
        story_media_group.setLayout(story_media_layout)
        layout.addWidget(story_media_group)
        
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
        self.chapter_summary_text.setAcceptRichText(False)
        self.chapter_summary_text.setPlaceholderText("Chapter summary...")
        self.chapter_summary_text.setMinimumHeight(100)
        summary_layout.addWidget(self.chapter_summary_text)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Notes group
        notes_group = QGroupBox("Chapter Notes")
        notes_layout = QVBoxLayout()
        self.chapter_notes_text = QTextEdit()
        self.chapter_notes_text.setAcceptRichText(False)
        self.chapter_notes_text.setPlaceholderText("Plot points, reminders...")
        self.chapter_notes_text.setMinimumHeight(150)
        notes_layout.addWidget(self.chapter_notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Media group
        chapter_media_group = QGroupBox("Media")
        chapter_media_layout = QVBoxLayout()
        
        self.chapter_media_list = QListWidget()
        self.chapter_media_list.setMaximumHeight(120)
        chapter_media_layout.addWidget(self.chapter_media_list)
        
        chapter_media_btn_layout = QHBoxLayout()
        chapter_attach_media_btn = QPushButton("📎 Attach")
        chapter_attach_media_btn.clicked.connect(lambda: self._on_attach_media_generic('chapter'))
        chapter_media_btn_layout.addWidget(chapter_attach_media_btn)
        
        chapter_detach_media_btn = QPushButton("✂️ Detach")
        chapter_detach_media_btn.clicked.connect(lambda: self._on_detach_media_generic('chapter'))
        chapter_media_btn_layout.addWidget(chapter_detach_media_btn)
        
        chapter_media_layout.addLayout(chapter_media_btn_layout)
        chapter_media_group.setLayout(chapter_media_layout)
        layout.addWidget(chapter_media_group)
        
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
        
        # Buttons for relationship management
        btn_layout = QHBoxLayout()
        add_relationship_btn = QPushButton("➕ Add")
        add_relationship_btn.clicked.connect(self._on_add_relationship)
        btn_layout.addWidget(add_relationship_btn)
        
        edit_relationship_btn = QPushButton("✏️ Edit")
        edit_relationship_btn.clicked.connect(self._on_edit_relationship)
        btn_layout.addWidget(edit_relationship_btn)
        
        delete_relationship_btn = QPushButton("🗑️ Delete")
        delete_relationship_btn.clicked.connect(self._on_delete_relationship)
        btn_layout.addWidget(delete_relationship_btn)
        
        relationships_layout.addLayout(btn_layout)
        
        relationships_group.setLayout(relationships_layout)
        layout.addWidget(relationships_group)
        
        # Media group
        media_group = QGroupBox("Media")
        media_layout = QVBoxLayout()
        
        self.media_list = QListWidget()
        self.media_list.setMaximumHeight(150)
        self.media_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.media_list.setIconSize(QSize(64, 64))
        self.media_list.setSpacing(8)
        self.media_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.media_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.media_list.customContextMenuRequested.connect(self._on_media_context_menu)
        self.media_list.itemDoubleClicked.connect(self._on_media_double_clicked)
        media_layout.addWidget(self.media_list)
        
        # Buttons for media management
        media_btn_layout = QHBoxLayout()
        attach_media_btn = QPushButton("📎 Attach")
        attach_media_btn.clicked.connect(self._on_attach_media)
        media_btn_layout.addWidget(attach_media_btn)
        
        detach_media_btn = QPushButton("✂️ Detach")
        detach_media_btn.clicked.connect(self._on_detach_media)
        media_btn_layout.addWidget(detach_media_btn)
        
        media_layout.addLayout(media_btn_layout)
        
        media_group.setLayout(media_layout)
        layout.addWidget(media_group)
        
        # Notes group
        notes_group = QGroupBox("Character Notes")
        notes_layout = QVBoxLayout()
        self.character_notes_text = QTextEdit()
        self.character_notes_text.setAcceptRichText(False)
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
        self.scene_summary_text.setAcceptRichText(False)
        self.scene_summary_text.setPlaceholderText("Brief summary of this scene...")
        self.scene_summary_text.setMaximumHeight(100)
        
        summary_layout.addWidget(self.scene_summary_text)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Notes group
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        
        self.scene_notes_text = QTextEdit()
        self.scene_notes_text.setAcceptRichText(False)
        self.scene_notes_text.setPlaceholderText("Research notes, ideas, reminders...")
        self.scene_notes_text.setMaximumHeight(150)
        
        notes_layout.addWidget(self.scene_notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Media group
        scene_media_group = QGroupBox("Media")
        scene_media_layout = QVBoxLayout()
        
        self.scene_media_list = QListWidget()
        self.scene_media_list.setMaximumHeight(120)
        scene_media_layout.addWidget(self.scene_media_list)
        
        scene_media_btn_layout = QHBoxLayout()
        scene_attach_media_btn = QPushButton("📎 Attach")
        scene_attach_media_btn.clicked.connect(lambda: self._on_attach_media_generic('scene'))
        scene_media_btn_layout.addWidget(scene_attach_media_btn)
        
        scene_detach_media_btn = QPushButton("✂️ Detach")
        scene_detach_media_btn.clicked.connect(lambda: self._on_detach_media_generic('scene'))
        scene_media_btn_layout.addWidget(scene_detach_media_btn)
        
        scene_media_layout.addLayout(scene_media_btn_layout)
        scene_media_group.setLayout(scene_media_layout)
        layout.addWidget(scene_media_group)
        
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
        
        # Load media attachments
        self.project_media_list.clear()
        try:
            media_items = self.app_context.media_service.get_entity_media('project', project.id)
            for media in media_items:
                icon_map = {"image": "🖼️", "audio": "🎵", "video": "🎬"}
                icon = icon_map.get(media.media_type, "📄")
                display_text = f"{icon} {media.get_display_title()}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, media.id)
                self.project_media_list.addItem(item)
        except Exception as e:
            print(f"Failed to load project media: {e}")
        
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
        
        # Load media attachments
        self.story_media_list.clear()
        try:
            media_items = self.app_context.media_service.get_entity_media('story', story.id)
            for media in media_items:
                icon_map = {"image": "🖼️", "audio": "🎵", "video": "🎬"}
                icon = icon_map.get(media.media_type, "📄")
                display_text = f"{icon} {media.get_display_title()}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, media.id)
                self.story_media_list.addItem(item)
        except Exception as e:
            print(f"Failed to load story media: {e}")
        
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
        
        # Load media attachments
        self.chapter_media_list.clear()
        try:
            media_items = self.app_context.media_service.get_entity_media('chapter', chapter.id)
            for media in media_items:
                icon_map = {"image": "🖼️", "audio": "🎵", "video": "🎬"}
                icon = icon_map.get(media.media_type, "📄")
                display_text = f"{icon} {media.get_display_title()}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, media.id)
                self.chapter_media_list.addItem(item)
        except Exception as e:
            print(f"Failed to load chapter media: {e}")
        
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
        
        # Load relationships from database
        self.relationships_list.clear()
        
        try:
            # Load interpersonal relationships using service
            interpersonal_rels = self.app_context.relationship_service.get_character_relationships(character.id)
            
            for rel in interpersonal_rels:
                # Determine which character is the "other"
                other_id = rel.character_b_id if rel.character_a_id == character.id else rel.character_a_id
                other_char = self.app_context._session.query(Character).filter(
                    Character.id == other_id
                ).first()
                
                if other_char:
                    other_name = other_char.nickname or other_char.first_name or f"Character {other_char.id}"
                    display_text = f"{rel.relationship_type}: {other_name}"
                    item = QListWidgetItem(display_text)
                    # Store relationship data for editing/deletion
                    item.setData(Qt.ItemDataRole.UserRole, {'type': 'interpersonal', 'id': rel.id})
                    self.relationships_list.addItem(item)
            
            # Load symbolic/motif relationships
            motif_rels = self.app_context._session.query(CharacterMotifRelationship).filter(
                CharacterMotifRelationship.character_id == character.id
            ).all()
            
            for motif_rel in motif_rels:
                motif = self.app_context._session.query(SymbolicMotif).filter(
                    SymbolicMotif.id == motif_rel.motif_id
                ).first()
                
                if motif:
                    display_text = f"🔮 {motif.name}"
                    item = QListWidgetItem(display_text)
                    # Store relationship data for editing/deletion
                    item.setData(Qt.ItemDataRole.UserRole, {'type': 'symbolic', 'id': motif_rel.id})
                    self.relationships_list.addItem(item)
        
        except Exception as e:
            # Fall back to meta if database query fails
            if character.meta and 'relationships' in character.meta:
                for rel in character.meta['relationships']:
                    self.relationships_list.addItem(rel)
        
        # Load media attachments
        self.media_list.clear()
        try:
            media_items = self.app_context.media_service.get_entity_media('character', character.id)
            for media in media_items:
                display_text = media.title or media.original_filename
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, media.id)
                
                # Add thumbnail for images
                if media.media_type == 'image':
                    from pathlib import Path
                    from PySide6.QtGui import QPixmap, QIcon
                    
                    # Try thumbnail first, then original
                    thumb_path = Path(media.thumbnail_path) if media.thumbnail_path else None
                    img_path = Path(media.file_path) if not thumb_path or not thumb_path.exists() else thumb_path
                    
                    if img_path and img_path.exists():
                        pixmap = QPixmap(str(img_path))
                        if not pixmap.isNull():
                            # Scale to thumbnail size
                            scaled = pixmap.scaled(
                                64, 64,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation
                            )
                            item.setIcon(QIcon(scaled))
                
                self.media_list.addItem(item)
        except Exception as e:
            print(f"Failed to load media: {e}")
        
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
        
        # Load media attachments
        self.scene_media_list.clear()
        try:
            media_items = self.app_context.media_service.get_entity_media('scene', scene.id)
            for media in media_items:
                icon_map = {"image": "🖼️", "audio": "🎵", "video": "🎬"}
                icon = icon_map.get(media.media_type, "📄")
                display_text = f"{icon} {media.get_display_title()}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, media.id)
                self.scene_media_list.addItem(item)
        except Exception as e:
            print(f"Failed to load scene media: {e}")
        
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
        
        character = self.current_context
        
        # Get project to access other characters and motifs
        project = self.app_context.project_service.get_project(character.project_id)
        if not project:
            return
        
        # Get available characters for interpersonal relationships
        available_characters = self.app_context.character_service.list_characters(project.id)
        
        # Get available motifs for symbolic relationships  
        # TODO: Add motif service when implemented
        available_motifs = []
        try:
            from nico.infrastructure.database.repositories import SymbolicMotifRepository
            motif_repo = SymbolicMotifRepository(self.app_context.db_session)
            available_motifs = motif_repo.list_by_project(project.id)
        except Exception:
            pass  # Motif repository may not be implemented yet
        
        # Show relationship dialog
        dialog = RelationshipDialog(
            character=character,
            project_id=project.id,
            available_characters=available_characters,
            available_motifs=available_motifs,
            parent=self
        )
        
        if dialog.exec() == dialog.DialogCode.Accepted:
            rel_data = dialog.get_relationship_data()
            if not rel_data:
                return
            
            try:
                if rel_data['type'] == 'interpersonal':
                    # Create character-to-character relationship using service
                    relationship = self.app_context.relationship_service.create_relationship(
                        project_id=project.id,
                        character_a_id=rel_data['character_a_id'],
                        character_b_id=rel_data['character_b_id'],
                        relationship_type=rel_data['relationship_type'],
                        description=rel_data.get('description'),
                        attributes=rel_data.get('attributes'),
                        status=rel_data.get('status'),
                        began_at=rel_data.get('began_at'),
                    )
                    
                    # Display in list
                    other_char = next(
                        (c for c in available_characters if c.id == rel_data['character_b_id']),
                        None
                    )
                    if other_char:
                        other_name = other_char.nickname or other_char.first_name or f"Character {other_char.id}"
                        display_text = f"{rel_data['relationship_type']}: {other_name}"
                        item = QListWidgetItem(display_text)
                        item.setData(Qt.ItemDataRole.UserRole, {'type': 'interpersonal', 'id': relationship.id})
                        self.relationships_list.addItem(item)
                
                elif rel_data['type'] == 'symbolic':
                    # Create character-to-motif relationship
                    # Access the internal session for now (until we have a symbolic service)
                    char_motif_rel = CharacterMotifRelationship(
                        character_id=rel_data['character_id'],
                        motif_id=rel_data['motif_id'],
                        description=rel_data.get('description'),
                        attributes=rel_data.get('attributes'),
                    )
                    self.app_context._session.add(char_motif_rel)
                    self.app_context._session.commit()
                    
                    # Display in list
                    motif = next(
                        (m for m in available_motifs if m.id == rel_data['motif_id']),
                        None
                    )
                    if motif:
                        display_text = f"🔮 {motif.name}"
                        item = QListWidgetItem(display_text)
                        item.setData(Qt.ItemDataRole.UserRole, {'type': 'symbolic', 'id': char_motif_rel.id})
                        self.relationships_list.addItem(item)
                
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error Creating Relationship",
                    f"Failed to create relationship: {str(e)}"
                )
    
    def _on_edit_relationship(self):
        """Edit selected relationship."""
        if not isinstance(self.current_context, Character):
            return
        
        current_item = self.relationships_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a relationship to edit.")
            return
        
        rel_metadata = current_item.data(Qt.ItemDataRole.UserRole)
        if not rel_metadata:
            return
        
        character = self.current_context
        project = self.app_context.project_service.get_project(character.project_id)
        if not project:
            return
        
        # Load the relationship to edit
        edit_relationship = None
        if rel_metadata['type'] == 'interpersonal':
            edit_relationship = self.app_context.relationship_service.get_relationship(rel_metadata['id'])
        elif rel_metadata['type'] == 'symbolic':
            edit_relationship = self.app_context._session.query(CharacterMotifRelationship).filter(
                CharacterMotifRelationship.id == rel_metadata['id']
            ).first()
        
        if not edit_relationship:
            QMessageBox.warning(self, "Not Found", "Could not find relationship to edit.")
            return
        
        # Get available characters and motifs
        available_characters = self.app_context.character_service.list_characters(project.id)
        available_motifs = []
        try:
            from nico.infrastructure.database.repositories import SymbolicMotifRepository
            motif_repo = SymbolicMotifRepository(self.app_context._session)
            available_motifs = motif_repo.list_by_project(project.id)
        except Exception:
            pass
        
        # Show dialog with existing data
        dialog = RelationshipDialog(
            character=character,
            project_id=project.id,
            available_characters=available_characters,
            available_motifs=available_motifs,
            edit_relationship=edit_relationship,
            parent=self
        )
        
        if dialog.exec() == dialog.DialogCode.Accepted:
            rel_data = dialog.get_relationship_data()
            if not rel_data or not rel_data.get('id'):
                return
            
            try:
                if rel_data['type'] == 'interpersonal':
                    # Update interpersonal relationship
                    relationship = self.app_context.relationship_service.get_relationship(rel_data['id'])
                    if relationship:
                        relationship.relationship_type = rel_data['relationship_type']
                        relationship.description = rel_data.get('description')
                        relationship.attributes = rel_data.get('attributes')
                        relationship.status = rel_data.get('status')
                        relationship.began_at = rel_data.get('began_at')
                        self.app_context._session.commit()
                        
                        # Update display
                        other_char = next(
                            (c for c in available_characters if c.id == rel_data['character_b_id']),
                            None
                        )
                        if other_char:
                            other_name = other_char.nickname or other_char.first_name or f"Character {other_char.id}"
                            current_item.setText(f"{rel_data['relationship_type']}: {other_name}")
                
                elif rel_data['type'] == 'symbolic':
                    # Update symbolic relationship
                    char_motif_rel = self.app_context._session.query(CharacterMotifRelationship).filter(
                        CharacterMotifRelationship.id == rel_data['id']
                    ).first()
                    if char_motif_rel:
                        char_motif_rel.description = rel_data.get('description')
                        char_motif_rel.attributes = rel_data.get('attributes')
                        self.app_context._session.commit()
                        
                        # Update display (motif shouldn't change, but attributes might)
                        motif = next(
                            (m for m in available_motifs if m.id == rel_data['motif_id']),
                            None
                        )
                        if motif:
                            current_item.setText(f"🔮 {motif.name}")
                
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error Updating Relationship",
                    f"Failed to update relationship: {str(e)}"
                )
    
    def _on_delete_relationship(self):
        """Delete selected relationship."""
        if not isinstance(self.current_context, Character):
            return
        
        current_item = self.relationships_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a relationship to delete.")
            return
        
        rel_metadata = current_item.data(Qt.ItemDataRole.UserRole)
        if not rel_metadata:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete this relationship?\n\n{current_item.text()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if rel_metadata['type'] == 'interpersonal':
                    # Delete via service
                    relationship = self.app_context.relationship_service.get_relationship(rel_metadata['id'])
                    if relationship:
                        self.app_context._session.delete(relationship)
                        self.app_context._session.commit()
                        
                elif rel_metadata['type'] == 'symbolic':
                    # Delete symbolic relationship
                    char_motif_rel = self.app_context._session.query(CharacterMotifRelationship).filter(
                        CharacterMotifRelationship.id == rel_metadata['id']
                    ).first()
                    if char_motif_rel:
                        self.app_context._session.delete(char_motif_rel)
                        self.app_context._session.commit()
                
                # Remove from list
                row = self.relationships_list.row(current_item)
                self.relationships_list.takeItem(row)
                
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error Deleting Relationship",
                    f"Failed to delete relationship: {str(e)}"
                )
    
    def _on_attach_media(self):
        """Attach media to the current entity."""
        if not isinstance(self.current_context, Character):
            return
        
        character = self.current_context
        
        dialog = MediaPickerDialog(
            project_id=character.project_id,
            app_context=self.app_context,
            entity_type='character',
            entity_id=character.id,
            parent=self
        )
        
        if dialog.exec() == dialog.DialogCode.Accepted:
            # Reload character to refresh media list
            self.load_character(character)
    
    def _on_detach_media(self):
        """Detach selected media from the current entity."""
        if not isinstance(self.current_context, Character):
            return
        
        current_item = self.media_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select media to detach.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Detachment",
            f"Are you sure you want to detach this media?\n\n{current_item.text()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                media_id = current_item.data(Qt.ItemDataRole.UserRole)
                
                # Find and delete the attachment
                from nico.domain.models import MediaAttachment
                attachment = self.app_context._session.query(MediaAttachment).filter(
                    MediaAttachment.media_id == media_id,
                    MediaAttachment.entity_type == 'character',
                    MediaAttachment.entity_id == self.current_context.id
                ).first()
                
                if attachment:
                    self.app_context.media_service.detach_media_from_entity(attachment.id)
                    
                    # Remove from list
                    row = self.media_list.row(current_item)
                    self.media_list.takeItem(row)
                    
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error Detaching Media",
                    f"Failed to detach media: {str(e)}"
                )
    
    def _on_media_context_menu(self, position) -> None:
        """Show context menu for media item."""
        if not isinstance(self.current_context, Character):
            return
        
        item = self.media_list.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        view_action = menu.addAction("👁️ View")
        view_action.triggered.connect(lambda: self._on_view_media(item))
        
        menu.addSeparator()
        
        detach_action = menu.addAction("✂️ Detach")
        detach_action.triggered.connect(self._on_detach_media)
        
        menu.exec(self.media_list.mapToGlobal(position))
    
    def _on_media_double_clicked(self, item) -> None:
        """View media on double-click."""
        self._on_view_media(item)
    
    def _on_view_media(self, item) -> None:
        """View the selected media item."""
        if not item:
            return
        
        media_id = item.data(Qt.ItemDataRole.UserRole)
        if not media_id:
            return
        
        # Get the media
        from nico.domain.models import Media
        media = self.app_context._session.query(Media).filter(
            Media.id == media_id
        ).first()
        
        if not media:
            return
        
        from pathlib import Path
        media_path = Path(media.file_path)
        
        if not media_path.exists():
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Media file not found:\n{media_path}"
            )
            return
        
        # Open with system default application
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(media_path.absolute())))
    
    def _on_attach_media_generic(self, entity_type: str):
        """Attach media to the current entity (generic handler for all entity types)."""
        if not self.current_context:
            return
        
        # Determine project_id based on entity hierarchy
        project_id = None
        if entity_type == 'project':
            project_id = self.current_context.id
        elif hasattr(self.current_context, 'project_id'):
            # Story has direct project_id
            project_id = self.current_context.project_id
        elif entity_type == 'chapter' and hasattr(self.current_context, 'story'):
            # Chapter -> Story -> Project
            project_id = self.current_context.story.project_id
        elif entity_type == 'scene' and hasattr(self.current_context, 'chapter'):
            # Scene -> Chapter -> Story -> Project
            project_id = self.current_context.chapter.story.project_id
        
        if not project_id:
            QMessageBox.warning(self, "Error", "Cannot determine project for media attachment.")
            return
        
        dialog = MediaPickerDialog(
            project_id=project_id,
            app_context=self.app_context,
            entity_type=entity_type,
            entity_id=self.current_context.id,
            parent=self
        )
        
        if dialog.exec() == dialog.DialogCode.Accepted:
            # Reload the current entity to refresh media list
            if entity_type == 'project':
                self.load_project(self.current_context)
            elif entity_type == 'story':
                self.load_story(self.current_context)
            elif entity_type == 'chapter':
                self.load_chapter(self.current_context)
            elif entity_type == 'scene':
                self.load_scene(self.current_context)
    
    def _on_detach_media_generic(self, entity_type: str):
        """Detach selected media from the current entity (generic handler for all entity types)."""
        if not self.current_context:
            return
        
        # Get the appropriate media list widget
        media_list_map = {
            'project': self.project_media_list,
            'story': self.story_media_list,
            'chapter': self.chapter_media_list,
            'scene': self.scene_media_list,
        }
        
        media_list = media_list_map.get(entity_type)
        if not media_list:
            return
        
        current_item = media_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select media to detach.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Detachment",
            f"Are you sure you want to detach this media?\n\n{current_item.text()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                media_id = current_item.data(Qt.ItemDataRole.UserRole)
                
                # Find and delete the attachment
                from nico.domain.models import MediaAttachment
                attachment = self.app_context._session.query(MediaAttachment).filter(
                    MediaAttachment.media_id == media_id,
                    MediaAttachment.entity_type == entity_type,
                    MediaAttachment.entity_id == self.current_context.id
                ).first()
                
                if attachment:
                    self.app_context.media_service.detach_media_from_entity(attachment.id)
                    
                    # Remove from list
                    row = media_list.row(current_item)
                    media_list.takeItem(row)
                    
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error Detaching Media",
                    f"Failed to detach media: {str(e)}"
                )
    
    def clear(self) -> None:
        """Clear all inspector fields and show empty state."""
        self.current_context = None
        self.current_context_type = None
        self.title_label.setText("🔍 Inspector")
        self.stack.setCurrentWidget(self.empty_page)
