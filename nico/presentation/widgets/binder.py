"""Binder widget - project tree navigation."""
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QTreeWidgetItemIterator,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
)
from PySide6.QtGui import QAction

from nico.domain.models import Project, Story, Chapter, Scene
from nico.application.context import get_app_context


class BinderWidget(QWidget):
    """Left panel: Project tree/binder for navigation."""
    
    # Signals emitted when items are selected
    project_selected = Signal(int)  # project_id
    story_selected = Signal(int)  # story_id
    chapter_selected = Signal(int)  # chapter_id
    scene_selected = Signal(int)  # scene_id
    character_selected = Signal(int)  # character_id
    location_selected = Signal(int)  # location_id
    event_selected = Signal(int)  # event_id
    
    # Signals for collection nodes
    stories_collection_selected = Signal()  # When "Stories" node is clicked
    characters_collection_selected = Signal()  # When "Characters" node is clicked
    locations_collection_selected = Signal()  # When "Locations" node is clicked
    events_collection_selected = Signal()  # When "Events" node is clicked
    
    # Signal emitted when an item is deleted
    item_deleted = Signal(str)  # item_type ("story", "chapter", "scene", "character", etc.)
    
    def __init__(self) -> None:
        super().__init__()
        self.current_project: Optional[Project] = None
        self.app_context = get_app_context()
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("📚 Binder")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search project...")
        layout.addWidget(self.search_box)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.tree)
        
        self.setLayout(layout)
    
    def load_project(self, project: Project) -> None:
        """Load a project into the binder tree."""
        self.current_project = project
        self.tree.clear()
        
        # Project root
        project_item = QTreeWidgetItem(self.tree, [f"📚 {project.title}"])
        project_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "project", "id": project.id})
        project_item.setExpanded(True)
        
        # Store reference to project item for programmatic selection
        self.project_item = project_item
        
        # Stories node
        stories_node = QTreeWidgetItem(project_item, ["📚 Stories"])
        stories_node.setData(0, Qt.ItemDataRole.UserRole, {"type": "stories_collection", "id": None})
        stories_node.setExpanded(True)
        
        # Stories
        for story in project.stories:
            story_item = QTreeWidgetItem(stories_node, [f"📖 {story.title}"])
            story_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "story", "id": story.id})
            story_item.setExpanded(False)
            
            # Chapters
            for chapter in story.chapters:
                chapter_item = QTreeWidgetItem(
                    story_item,
                    [f"📑 Chapter {chapter.number}: {chapter.title}"]
                )
                chapter_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "chapter", "id": chapter.id})
                chapter_item.setExpanded(False)
                
                # Scenes
                for scene in chapter.scenes:
                    scene_item = QTreeWidgetItem(chapter_item, [f"✍️ {scene.title}"])
                    scene_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "scene", "id": scene.id})
        
        # Characters node
        characters_node = QTreeWidgetItem(project_item, ["🎭 Characters"])
        characters_node.setData(0, Qt.ItemDataRole.UserRole, {"type": "characters_collection", "id": None})
        characters_node.setExpanded(False)
        
        # Load actual characters
        characters = self.app_context.character_service.list_characters(project.id)
        if characters:
            for char in characters:
                name = char.nickname or char.first_name or "Unnamed"
                if char.last_name:
                    name += f" {char.last_name}"
                char_item = QTreeWidgetItem(characters_node, [f"👤 {name}"])
                char_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "character", "id": char.id})
        else:
            placeholder_char = QTreeWidgetItem(characters_node, ["No characters yet"])
            placeholder_char.setData(0, Qt.ItemDataRole.UserRole, {"type": "placeholder", "id": None})
        
        # Locations node
        locations_node = QTreeWidgetItem(project_item, ["🗺️ Locations"])
        locations_node.setData(0, Qt.ItemDataRole.UserRole, {"type": "locations_collection", "id": None})
        locations_node.setExpanded(False)
        
        # Load actual locations
        locations = self.app_context.location_service.list_locations(project.id)
        if locations:
            for loc in locations:
                loc_item = QTreeWidgetItem(locations_node, [f"📍 {loc.name}"])
                loc_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "location", "id": loc.id})
        else:
            placeholder_loc = QTreeWidgetItem(locations_node, ["No locations yet"])
            placeholder_loc.setData(0, Qt.ItemDataRole.UserRole, {"type": "placeholder", "id": None})
        
        # Events node
        events_node = QTreeWidgetItem(project_item, ["📅 Events"])
        events_node.setData(0, Qt.ItemDataRole.UserRole, {"type": "events_collection", "id": None})
        events_node.setExpanded(False)
        
        # Load actual events
        events = self.app_context.event_service.list_events(project.id)
        if events:
            for event in events:
                event_item = QTreeWidgetItem(events_node, [f"📅 {event.title}"])
                event_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "event", "id": event.id})
        else:
            placeholder_event = QTreeWidgetItem(events_node, ["No events yet"])
            placeholder_event.setData(0, Qt.ItemDataRole.UserRole, {"type": "placeholder", "id": None})
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle tree item click."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
            
        item_type = data["type"]
        item_id = data["id"]
        
        # Handle collection nodes
        if item_type == "stories_collection":
            self.stories_collection_selected.emit()
            return
        elif item_type == "characters_collection":
            self.characters_collection_selected.emit()
            return
        elif item_type == "locations_collection":
            self.locations_collection_selected.emit()
            return
        elif item_type == "events_collection":
            self.events_collection_selected.emit()
            return
        elif item_type == "placeholder":
            return
        
        # Handle individual items
        if item_type == "project":
            self.project_selected.emit(item_id)
        elif item_type == "story":
            self.story_selected.emit(item_id)
        elif item_type == "chapter":
            self.chapter_selected.emit(item_id)
        elif item_type == "scene":
            self.scene_selected.emit(item_id)
        elif item_type == "character":
            self.character_selected.emit(item_id)
        elif item_type == "location":
            self.location_selected.emit(item_id)
        elif item_type == "event":
            self.event_selected.emit(item_id)
    
    def _find_item_by_data(self, item_type: str, item_id: int) -> Optional[QTreeWidgetItem]:
        """Find a tree item by its type and id."""
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and data.get("type") == item_type and data.get("id") == item_id:
                return item
            iterator += 1
        return None
    
    def select_project(self, project_id: int) -> None:
        """Programmatically select a project item in the tree."""
        item = self._find_item_by_data("project", project_id)
        if item:
            self.tree.setCurrentItem(item)
    
    def select_story(self, story_id: int) -> None:
        """Programmatically select a story item in the tree."""
        item = self._find_item_by_data("story", story_id)
        if item:
            # Expand parent items to make it visible
            parent = item.parent()
            while parent:
                parent.setExpanded(True)
                parent = parent.parent()
            self.tree.setCurrentItem(item)
    
    def select_chapter(self, chapter_id: int) -> None:
        """Programmatically select a chapter item in the tree."""
        item = self._find_item_by_data("chapter", chapter_id)
        if item:
            # Expand parent items to make it visible
            parent = item.parent()
            while parent:
                parent.setExpanded(True)
                parent = parent.parent()
            self.tree.setCurrentItem(item)
    
    def select_scene(self, scene_id: int) -> None:
        """Programmatically select a scene item in the tree."""
        item = self._find_item_by_data("scene", scene_id)
        if item:
            # Expand parent items to make it visible
            parent = item.parent()
            while parent:
                parent.setExpanded(True)
                parent = parent.parent()
            self.tree.setCurrentItem(item)
    
    def _show_context_menu(self, position) -> None:
        """Show context menu for tree items."""
        item = self.tree.itemAt(position)
        if not item:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        item_type = data.get("type")
        item_id = data.get("id")
        
        # Only show context menu for specific item types
        if item_type not in ("scene", "chapter", "story", "character", "location", "event"):
            return
        
        menu = QMenu(self)
        
        # Delete action
        delete_action = QAction("🗑️ Delete", self)
        delete_action.triggered.connect(lambda: self._delete_item(item_type, item_id, item))
        menu.addAction(delete_action)
        
        menu.exec(self.tree.viewport().mapToGlobal(position))
    
    def _delete_item(self, item_type: str, item_id: int, tree_item: QTreeWidgetItem) -> None:
        """Delete an item from the tree."""
        # Get item name for confirmation
        item_name = tree_item.text(0)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            f"Delete {item_type.capitalize()}",
            f"Are you sure you want to delete {item_name}?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Delete based on type
            success = False
            if item_type == "scene":
                scene = self.app_context.scene_service.get_scene(item_id)
                if scene:
                    # Access repository directly through the service's repo
                    self.app_context.scene_service.scene_repo.delete(item_id)
                    success = True
            elif item_type == "chapter":
                # Get chapter through project hierarchy
                chapter = None
                if self.current_project:
                    for story in self.current_project.stories:
                        chapter = next((c for c in story.chapters if c.id == item_id), None)
                        if chapter:
                            break
                if chapter:
                    # Delete chapter using session directly
                    if hasattr(self.app_context, '_session') and self.app_context._session:
                        self.app_context._session.delete(chapter)
                        success = True
            elif item_type == "story":
                # Get story through project
                story = None
                if self.current_project:
                    story = next((s for s in self.current_project.stories if s.id == item_id), None)
                if story:
                    # Delete story using session directly
                    if hasattr(self.app_context, '_session') and self.app_context._session:
                        self.app_context._session.delete(story)
                        success = True
            elif item_type == "character":
                success = self.app_context.character_service.delete_character(item_id)
            elif item_type == "location":
                success = self.app_context.location_service.delete_location(item_id)
            elif item_type == "event":
                success = self.app_context.event_service.delete_event(item_id)
            
            if success:
                self.app_context.commit()
                # Reload the project from database to get fresh data
                if self.current_project:
                    refreshed_project = self.app_context.project_service.get_project(self.current_project.id)
                    if refreshed_project:
                        self.load_project(refreshed_project)
                
                # Emit signal so main window can handle showing appropriate overview
                self.item_deleted.emit(item_type)
                
                QMessageBox.information(
                    self,
                    f"{item_type.capitalize()} Deleted",
                    f"{item_name} has been deleted."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Delete Failed",
                    f"Could not delete {item_name}. It may have already been deleted."
                )
        except Exception as e:
            self.app_context.rollback()
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while deleting {item_name}:\n{str(e)}"
            )
