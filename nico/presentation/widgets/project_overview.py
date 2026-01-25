"""Project overview widget - landing page for project selection."""
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QMessageBox,
    QMenu,
    QToolButton,
)

from nico.domain.models import Project
from nico.application.context import get_app_context
from nico.presentation.widgets.character_dialog import CharacterDialog
from nico.presentation.widgets.location_dialog import LocationDialog
from nico.presentation.widgets.event_dialog import EventDialog
from nico.presentation.widgets.story_dialog import StoryDialog


class ProjectOverview(QWidget):
    """Landing page displayed when a project is selected in the binder."""
    
    # Signal emitted when user wants to edit the project
    project_edit_requested = Signal()
    # Signal emitted when project is deleted
    project_deleted = Signal()
    # Signal emitted when user wants to create a new story
    create_story_requested = Signal()
    # Signal emitted when user wants to edit a story
    story_edit_requested = Signal(int)  # story_id
    # Signal emitted when user clicks on a story in the list
    story_selected = Signal(int)  # story_id
    
    def __init__(self) -> None:
        super().__init__()
        self.current_project: Optional[Project] = None
        self.app_context = get_app_context()
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QVBoxLayout()
        
        # Title row with edit and delete buttons
        title_row = QHBoxLayout()
        self.title_label = QLabel("Project")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_row.addWidget(self.title_label)
        title_row.addStretch()
        
        self.edit_btn = QPushButton("✏️ Edit Project")
        self.edit_btn.clicked.connect(self._on_edit_project)
        title_row.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete Project")
        self.delete_btn.clicked.connect(self._on_delete_project)
        title_row.addWidget(self.delete_btn)
        
        header.addLayout(title_row)
        
        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #666; font-size: 14px;")
        header.addWidget(self.description_label)
        
        layout.addLayout(header)
        
        # Statistics group
        stats_group = QGroupBox("Project Statistics")
        stats_layout = QGridLayout()
        
        self.stories_stat = QLabel("0")
        self.stories_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Stories:"), 0, 0)
        stats_layout.addWidget(self.stories_stat, 0, 1)
        
        self.chapters_stat = QLabel("0")
        self.chapters_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Chapters:"), 0, 2)
        stats_layout.addWidget(self.chapters_stat, 0, 3)
        
        self.scenes_stat = QLabel("0")
        self.scenes_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Scenes:"), 0, 4)
        stats_layout.addWidget(self.scenes_stat, 0, 5)
        
        self.word_count_stat = QLabel("0")
        self.word_count_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Total Words:"), 1, 0)
        stats_layout.addWidget(self.word_count_stat, 1, 1)
        
        self.characters_stat = QLabel("0")
        self.characters_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Characters:"), 1, 2)
        stats_layout.addWidget(self.characters_stat, 1, 3)
        
        self.locations_stat = QLabel("0")
        self.locations_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Locations:"), 1, 4)
        stats_layout.addWidget(self.locations_stat, 1, 5)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Stories list group
        stories_group = QGroupBox("Stories in this Project")
        stories_layout = QVBoxLayout()
        
        # Create/edit story buttons
        create_btn_layout = QHBoxLayout()
        self.create_story_btn = QPushButton("➕ New Story")
        self.create_story_btn.clicked.connect(self._on_create_story)
        create_btn_layout.addWidget(self.create_story_btn)
        
        self.edit_story_btn = QPushButton("✏️ Edit Story")
        self.edit_story_btn.clicked.connect(self._on_edit_story_clicked)
        create_btn_layout.addWidget(self.edit_story_btn)
        
        create_btn_layout.addStretch()
        stories_layout.addLayout(create_btn_layout)
        
        # Stories list with reordering controls
        list_layout = QHBoxLayout()
        
        self.stories_list = QListWidget()
        self.stories_list.itemDoubleClicked.connect(self._on_story_double_clicked)
        self.stories_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.stories_list.customContextMenuRequested.connect(self._show_story_context_menu)
        list_layout.addWidget(self.stories_list)
        
        # Reorder buttons
        reorder_buttons = QVBoxLayout()
        self.story_move_up_btn = QToolButton()
        self.story_move_up_btn.setText("▲")
        self.story_move_up_btn.setToolTip("Move story up")
        self.story_move_up_btn.clicked.connect(self._move_story_up)
        reorder_buttons.addWidget(self.story_move_up_btn)
        
        self.story_move_down_btn = QToolButton()
        self.story_move_down_btn.setText("▼")
        self.story_move_down_btn.setToolTip("Move story down")
        self.story_move_down_btn.clicked.connect(self._move_story_down)
        reorder_buttons.addWidget(self.story_move_down_btn)
        
        reorder_buttons.addStretch()
        list_layout.addLayout(reorder_buttons)
        
        stories_layout.addLayout(list_layout)
        
        stories_group.setLayout(stories_layout)
        layout.addWidget(stories_group)
        
        # Characters list group
        characters_group = QGroupBox("Characters in this Project")
        characters_layout = QVBoxLayout()
        
        # Create/edit character buttons
        create_char_btn_layout = QHBoxLayout()
        self.create_character_btn = QPushButton("➕ New Character")
        self.create_character_btn.clicked.connect(self._on_create_character)
        create_char_btn_layout.addWidget(self.create_character_btn)
        
        self.edit_character_btn = QPushButton("✏️ Edit Character")
        self.edit_character_btn.clicked.connect(self._on_edit_character_clicked)
        create_char_btn_layout.addWidget(self.edit_character_btn)
        
        create_char_btn_layout.addStretch()
        characters_layout.addLayout(create_char_btn_layout)
        
        # Characters list
        self.characters_list = QListWidget()
        self.characters_list.setMaximumHeight(150)
        self.characters_list.itemDoubleClicked.connect(self._on_character_double_clicked)
        characters_layout.addWidget(self.characters_list)
        
        characters_group.setLayout(characters_layout)
        layout.addWidget(characters_group)
        
        # Locations list group
        locations_group = QGroupBox("Locations in this Project")
        locations_layout = QVBoxLayout()
        
        # Create/edit location buttons
        create_loc_btn_layout = QHBoxLayout()
        self.create_location_btn = QPushButton("➕ New Location")
        self.create_location_btn.clicked.connect(self._on_create_location)
        create_loc_btn_layout.addWidget(self.create_location_btn)
        
        self.edit_location_btn = QPushButton("✏️ Edit Location")
        self.edit_location_btn.clicked.connect(self._on_edit_location_clicked)
        create_loc_btn_layout.addWidget(self.edit_location_btn)
        
        create_loc_btn_layout.addStretch()
        locations_layout.addLayout(create_loc_btn_layout)
        
        # Locations list
        self.locations_list = QListWidget()
        self.locations_list.setMaximumHeight(150)
        self.locations_list.itemDoubleClicked.connect(self._on_location_double_clicked)
        locations_layout.addWidget(self.locations_list)
        
        locations_group.setLayout(locations_layout)
        layout.addWidget(locations_group)
        
        # Events list group
        events_group = QGroupBox("Events in this Project")
        events_layout = QVBoxLayout()
        
        # Create/edit event buttons
        create_event_btn_layout = QHBoxLayout()
        self.create_event_btn = QPushButton("➕ New Event")
        self.create_event_btn.clicked.connect(self._on_create_event)
        create_event_btn_layout.addWidget(self.create_event_btn)
        
        self.edit_event_btn = QPushButton("✏️ Edit Event")
        self.edit_event_btn.clicked.connect(self._on_edit_event_clicked)
        create_event_btn_layout.addWidget(self.edit_event_btn)
        
        create_event_btn_layout.addStretch()
        events_layout.addLayout(create_event_btn_layout)
        
        # Events list
        self.events_list = QListWidget()
        self.events_list.setMaximumHeight(150)
        self.events_list.itemDoubleClicked.connect(self._on_event_double_clicked)
        events_layout.addWidget(self.events_list)
        
        events_group.setLayout(events_layout)
        layout.addWidget(events_group)
        
        layout.addStretch()
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
    def load_project(self, project: Project) -> None:
        """Load project data into the overview."""
        self.current_project = project
        
        # Update header
        self.title_label.setText(f"📚 {project.title}")
        self.description_label.setText(project.description or "No description provided")
        
        # Calculate statistics
        total_chapters = sum(len(story.chapters) for story in project.stories)
        total_scenes = sum(
            len(chapter.scenes) 
            for story in project.stories 
            for chapter in story.chapters
        )
        total_words = sum(
            scene.word_count
            for story in project.stories
            for chapter in story.chapters
            for scene in chapter.scenes
        )
        
        # Update statistics
        self.stories_stat.setText(str(len(project.stories)))
        self.chapters_stat.setText(str(total_chapters))
        self.scenes_stat.setText(str(total_scenes))
        self.word_count_stat.setText(f"{total_words:,}")
        
        # Load worldbuilding entities
        self._load_characters()
        self._load_locations()
        self._load_events()
        
        # Update stories list
        self.stories_list.clear()
        for story in project.stories:
            chapter_count = len(story.chapters)
            scene_count = sum(len(chapter.scenes) for chapter in story.chapters)
            word_count = sum(
                scene.word_count
                for chapter in story.chapters
                for scene in chapter.scenes
            )
            
            item = QListWidgetItem(
                f"📖 {story.title}\n"
                f"   {chapter_count} chapters, {scene_count} scenes, {word_count:,} words"
            )
            item.setData(Qt.ItemDataRole.UserRole, story.id)
            self.stories_list.addItem(item)
    
    def _load_characters(self) -> None:
        """Load characters for the current project."""
        if not self.current_project:
            return
        
        characters = self.app_context.character_service.list_characters(self.current_project.id)
        self.characters_stat.setText(str(len(characters)))
        
        self.characters_list.clear()
        if characters:
            for char in characters:
                name = char.nickname or char.first_name or "Unnamed"
                if char.last_name:
                    name += f" {char.last_name}"
                item = QListWidgetItem(f"👤 {name}")
                item.setData(Qt.ItemDataRole.UserRole, char.id)
                self.characters_list.addItem(item)
        else:
            self.characters_list.addItem(QListWidgetItem("No characters yet - click '➕ New Character' to create"))
    
    def _load_locations(self) -> None:
        """Load locations for the current project."""
        if not self.current_project:
            return
        
        locations = self.app_context.location_service.list_locations(self.current_project.id)
        self.locations_stat.setText(str(len(locations)))
        
        self.locations_list.clear()
        if locations:
            for loc in locations:
                item = QListWidgetItem(f"📍 {loc.name}")
                item.setData(Qt.ItemDataRole.UserRole, loc.id)
                self.locations_list.addItem(item)
        else:
            self.locations_list.addItem(QListWidgetItem("No locations yet - click '➕ New Location' to create"))
    
    def _load_events(self) -> None:
        """Load events for the current project."""
        if not self.current_project:
            return
        
        events = self.app_context.event_service.list_events(self.current_project.id)
        
        self.events_list.clear()
        if events:
            for event in events:
                item = QListWidgetItem(f"📅 {event.title}")
                item.setData(Qt.ItemDataRole.UserRole, event.id)
                self.events_list.addItem(item)
        else:
            self.events_list.addItem(QListWidgetItem("No events yet - click '➕ New Event' to create"))
    
    def _on_create_character(self) -> None:
        """Handle create character button click."""
        if not self.current_project:
            return
        
        dialog = CharacterDialog(self.current_project.id, parent=self)
        if dialog.exec():
            self._load_characters()
    
    def _on_character_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on a character to edit."""
        character_id = item.data(Qt.ItemDataRole.UserRole)
        if not character_id or not self.current_project:
            return
        
        character = self.app_context.character_service.get_character(character_id)
        if character:
            dialog = CharacterDialog(self.current_project.id, character, parent=self)
            if dialog.exec():
                self._load_characters()
    
    def _on_edit_character_clicked(self) -> None:
        """Handle edit character button click."""
        current_item = self.characters_list.currentItem()
        if current_item:
            character_id = current_item.data(Qt.ItemDataRole.UserRole)
            if character_id:
                self._on_character_double_clicked(current_item)
    
    def _on_create_location(self) -> None:
        """Handle create location button click."""
        if not self.current_project:
            return
        
        dialog = LocationDialog(self.current_project.id, parent=self)
        if dialog.exec():
            self._load_locations()
    
    def _on_location_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on a location to edit."""
        location_id = item.data(Qt.ItemDataRole.UserRole)
        if not location_id or not self.current_project:
            return
        
        location = self.app_context.location_service.get_location(location_id)
        if location:
            dialog = LocationDialog(self.current_project.id, location, parent=self)
            if dialog.exec():
                self._load_locations()
    
    def _on_edit_location_clicked(self) -> None:
        """Handle edit location button click."""
        current_item = self.locations_list.currentItem()
        if current_item:
            location_id = current_item.data(Qt.ItemDataRole.UserRole)
            if location_id:
                self._on_location_double_clicked(current_item)
    
    def _on_create_event(self) -> None:
        """Handle create event button click."""
        if not self.current_project:
            return
        
        dialog = EventDialog(self.current_project.id, parent=self)
        if dialog.exec():
            self._load_events()
    
    def _on_event_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on an event to edit."""
        event_id = item.data(Qt.ItemDataRole.UserRole)
        if not event_id or not self.current_project:
            return
        
        event = self.app_context.event_service.get_event(event_id)
        if event:
            dialog = EventDialog(self.current_project.id, event, parent=self)
            if dialog.exec():
                self._load_events()
    
    def _on_edit_event_clicked(self) -> None:
        """Handle edit event button click."""
        current_item = self.events_list.currentItem()
        if current_item:
            event_id = current_item.data(Qt.ItemDataRole.UserRole)
            if event_id:
                self._on_event_double_clicked(current_item)
    
    def _on_story_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on a story."""
        story_id = item.data(Qt.ItemDataRole.UserRole)
        if story_id:
            self.story_selected.emit(story_id)
    
    def _on_create_story(self) -> None:
        """Handle create story button click."""
        if not self.current_project:
            return
        
        dialog = StoryDialog(self.current_project.id, parent=self)
        if dialog.exec():
            self.load_project(self.current_project)
    
    def _on_edit_project(self) -> None:
        """Handle edit project button click."""
        if self.current_project:
            self.project_edit_requested.emit()
    
    def _on_delete_project(self) -> None:
        """Delete the current project after confirmation."""
        if not self.current_project:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Project",
            f"Are you sure you want to delete '{self.current_project.title}'?\n\n"
            f"This will permanently delete ALL stories, chapters, scenes, characters, "
            f"locations, and events in this project.\n\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete the project using session directly
                if hasattr(self.app_context, '_session') and self.app_context._session:
                    self.app_context._session.delete(self.current_project)
                    self.app_context.commit()
                    self.current_project = None
                    self.project_deleted.emit()
                    QMessageBox.information(
                        self,
                        "Project Deleted",
                        "The project has been deleted."
                    )
            except Exception as e:
                self.app_context.rollback()
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while deleting the project:\n{str(e)}"
                )
    
    def _on_edit_story_clicked(self) -> None:
        """Handle edit story button click."""
        current_item = self.stories_list.currentItem()
        if current_item:
            story_id = current_item.data(Qt.ItemDataRole.UserRole)
            if story_id:
                self.story_edit_requested.emit(story_id)
    
    def _show_story_context_menu(self, position) -> None:
        """Show context menu for story list."""
        item = self.stories_list.itemAt(position)
        if not item:
            return
        
        story_id = item.data(Qt.ItemDataRole.UserRole)
        if not story_id:
            return
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("✏️ Edit Story")
        open_action = menu.addAction("📖 Open Story")
        
        action = menu.exec(self.stories_list.mapToGlobal(position))
        
        if action == edit_action:
            self.story_edit_requested.emit(story_id)
        elif action == open_action:
            self.story_selected.emit(story_id)
    
    def _move_story_up(self) -> None:
        """Move selected story up in the list."""
        current_row = self.stories_list.currentRow()
        if current_row > 0:
            item = self.stories_list.takeItem(current_row)
            self.stories_list.insertItem(current_row - 1, item)
            self.stories_list.setCurrentRow(current_row - 1)
            # TODO: Persist story order change to database
    
    def _move_story_down(self) -> None:
        """Move selected story down in the list."""
        current_row = self.stories_list.currentRow()
        if current_row < self.stories_list.count() - 1:
            item = self.stories_list.takeItem(current_row)
            self.stories_list.insertItem(current_row + 1, item)
            self.stories_list.setCurrentRow(current_row + 1)
            # TODO: Persist story order change to database
