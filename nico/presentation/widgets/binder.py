"""Binder widget - project tree navigation."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QLabel,
    QLineEdit,
)


class BinderWidget(QWidget):
    """Left panel: Project tree/binder for navigation."""
    
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self._populate_sample_data()
        
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
        layout.addWidget(self.tree)
        
        self.setLayout(layout)
        
    def _populate_sample_data(self) -> None:
        """Add sample tree structure."""
        # Project root
        project = QTreeWidgetItem(self.tree, ["📚 The Shadow Chronicles"])
        project.setExpanded(True)
        
        # Story
        story = QTreeWidgetItem(project, ["📖 Book One: The Awakening"])
        story.setExpanded(True)
        
        # Chapters
        chapter1 = QTreeWidgetItem(story, ["📑 Chapter 1: The Apprentice"])
        chapter1.setExpanded(True)
        
        # Scenes
        QTreeWidgetItem(chapter1, ["✍️ Morning in the Tower"])
        QTreeWidgetItem(chapter1, ["✍️ The Master's Lesson"])
        
        chapter2 = QTreeWidgetItem(story, ["📑 Chapter 2: The Discovery"])
        QTreeWidgetItem(chapter2, ["✍️ The Hidden Library"])
        
        # Worldbuilding section
        worldbuilding = QTreeWidgetItem(self.tree, ["🌍 Worldbuilding"])
        worldbuilding.setExpanded(True)
        
        characters = QTreeWidgetItem(worldbuilding, ["👥 Characters"])
        QTreeWidgetItem(characters, ["👤 Elara Windwhisper"])
        QTreeWidgetItem(characters, ["👤 Master Theron"])
        
        locations = QTreeWidgetItem(worldbuilding, ["🏰 Locations"])
        QTreeWidgetItem(locations, ["🏛️ The Ivory Tower"])
        
        events = QTreeWidgetItem(worldbuilding, ["⚡ Events"])
        QTreeWidgetItem(events, ["📅 Discovery of the Forbidden Tome"])
