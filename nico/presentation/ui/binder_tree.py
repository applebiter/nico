"""Binder tree widget for hierarchical project navigation."""

from typing import Optional
from uuid import UUID

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QTreeWidget, QTreeWidgetItem


class BinderItem(QTreeWidgetItem):
    """Tree item representing a project entity in the binder."""

    def __init__(self, item_type: str, item_id: Optional[UUID], title: str):
        super().__init__([title])
        self.item_type = item_type  # "project", "story", "chapter", "scene"
        self.item_id = item_id


class BinderTreeWidget(QTreeWidget):
    """Tree widget for displaying project hierarchy."""

    item_selected = Signal(str, UUID)  # (item_type, item_id)
    item_double_clicked = Signal(str, UUID)
    
    # Action signals for main window to handle
    add_story_requested = Signal()
    add_chapter_requested = Signal(UUID)  # story_id
    add_scene_requested = Signal(UUID)  # chapter_id
    delete_item_requested = Signal(str, UUID)  # (item_type, item_id)

    def __init__(self, parent: Optional[object] = None):
        super().__init__(parent)
        self.project_root: Optional[BinderItem] = None
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the tree widget."""
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

    def clear_project(self) -> None:
        """Clear all items from the tree."""
        self.clear()
        self.project_root = None

    def set_project(self, project_name: str) -> None:
        """Set the project root."""
        self.clear_project()
        self.project_root = BinderItem("project", None, project_name)
        self.addTopLevelItem(self.project_root)
        self.project_root.setExpanded(True)

    def add_story(self, story_id: UUID, title: str) -> BinderItem:
        """Add a story to the tree."""
        if not self.project_root:
            # Create implicit project root if not present
            self.project_root = BinderItem("project", None, "Project")
            self.addTopLevelItem(self.project_root)
            self.project_root.setExpanded(True)
        
        item = BinderItem("story", story_id, title)
        self.project_root.addChild(item)
        item.setExpanded(True)
        return item

    def add_chapter(self, story_item: BinderItem, chapter_id: UUID, title: str) -> BinderItem:
        """Add a chapter to a story."""
        item = BinderItem("chapter", chapter_id, title)
        story_item.addChild(item)
        story_item.setExpanded(True)
        return item

    def add_scene(self, chapter_item: BinderItem, scene_id: UUID, title: str) -> BinderItem:
        """Add a scene to a chapter."""
        item = BinderItem("scene", scene_id, title)
        chapter_item.addChild(item)
        chapter_item.setExpanded(True)
        return item

    def _on_selection_changed(self) -> None:
        """Handle selection change."""
        selected = self.selectedItems()
        if selected:
            item = selected[0]
            if isinstance(item, BinderItem) and item.item_id is not None:
                self.item_selected.emit(item.item_type, item.item_id)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle item double click."""
        if isinstance(item, BinderItem) and item.item_id is not None:
            self.item_double_clicked.emit(item.item_type, item.item_id)

    def _show_context_menu(self, position) -> None:
        """Show context menu for tree items."""
        item = self.itemAt(position)
        
        menu = QMenu(self)
        
        if item and isinstance(item, BinderItem):
            if item.item_type == "project":
                action = QAction("New Story", self)
                action.triggered.connect(lambda: self.add_story_requested.emit())
                menu.addAction(action)
            elif item.item_type == "story":
                action = QAction("New Chapter", self)
                action.triggered.connect(lambda: self.add_chapter_requested.emit(item.item_id))
                menu.addAction(action)
                menu.addSeparator()
                
                delete_action = QAction("Delete Story", self)
                delete_action.triggered.connect(lambda: self.delete_item_requested.emit("story", item.item_id))
                menu.addAction(delete_action)
            elif item.item_type == "chapter":
                action = QAction("New Scene", self)
                action.triggered.connect(lambda: self.add_scene_requested.emit(item.item_id))
                menu.addAction(action)
                menu.addSeparator()
                
                delete_action = QAction("Delete Chapter", self)
                delete_action.triggered.connect(lambda: self.delete_item_requested.emit("chapter", item.item_id))
                menu.addAction(delete_action)
            elif item.item_type == "scene":
                delete_action = QAction("Delete Scene", self)
                delete_action.triggered.connect(lambda: self.delete_item_requested.emit("scene", item.item_id))
                menu.addAction(delete_action)
        else:
            # No item selected - show project-level menu
            action = QAction("New Story", self)
            action.triggered.connect(lambda: self.add_story_requested.emit())
            menu.addAction(action)

        if not menu.isEmpty():
            menu.exec(self.viewport().mapToGlobal(position))
