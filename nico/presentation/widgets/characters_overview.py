"""Characters overview widget - listing page for all characters in a project."""
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
)

from nico.domain.models import Project, Character
from nico.application.context import get_app_context
from nico.presentation.widgets.character_dialog import CharacterDialog


class CharactersOverview(QWidget):
    """Landing page displayed when Characters collection is selected in the binder."""
    
    # Signal emitted when user wants to create a new character
    create_character_requested = Signal()
    # Signal emitted when user clicks on a character
    character_selected = Signal(int)  # character_id
    # Signal emitted when a character is created/updated
    character_updated = Signal()
    
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
        self.title_label = QLabel("🎭 Characters")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(self.title_label)
        
        self.description_label = QLabel("Manage the characters in your project")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #666; font-size: 14px;")
        header.addWidget(self.description_label)
        
        layout.addLayout(header)
        
        # Characters list group
        characters_group = QGroupBox("All Characters")
        characters_layout = QVBoxLayout()
        
        # Create character button
        create_btn_layout = QHBoxLayout()
        self.create_character_btn = QPushButton("➕ New Character")
        self.create_character_btn.clicked.connect(self._on_create_character)
        create_btn_layout.addWidget(self.create_character_btn)
        create_btn_layout.addStretch()
        characters_layout.addLayout(create_btn_layout)
        
        # Character list
        self.characters_list = QListWidget()
        self.characters_list.setMinimumHeight(300)
        self.characters_list.itemDoubleClicked.connect(self._on_character_double_clicked)
        characters_layout.addWidget(self.characters_list)
        
        characters_group.setLayout(characters_layout)
        layout.addWidget(characters_group)
        
        layout.addStretch()
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        # Set scroll area as the main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
    def load_project(self, project: Project) -> None:
        """Load characters for a project."""
        self.current_project = project
        self._refresh_characters()
        
    def _refresh_characters(self) -> None:
        """Refresh the characters list."""
        self.characters_list.clear()
        
        if not self.current_project:
            return
        
        # Get all characters
        characters = self.app_context.character_service.list_characters(self.current_project.id)
        
        if not characters:
            item = QListWidgetItem("No characters yet. Create one to get started!")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.characters_list.addItem(item)
            return
        
        # Add characters to list
        for char in characters:
            name = char.nickname or char.first_name or "Unnamed"
            if char.last_name:
                name += f" {char.last_name}"
            
            # Add occupation or description if available
            subtitle = ""
            if char.occupation:
                subtitle = char.occupation
            elif char.physical_description:
                subtitle = char.physical_description[:50] + ("..." if len(char.physical_description) > 50 else "")
            
            display_text = f"👤 {name}"
            if subtitle:
                display_text += f"\n   {subtitle}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, char.id)
            self.characters_list.addItem(item)
    
    def _on_character_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on character item."""
        character_id = item.data(Qt.ItemDataRole.UserRole)
        if character_id:
            self.character_selected.emit(character_id)
    
    def _on_create_character(self) -> None:
        """Open dialog to create a new character."""
        if not self.current_project:
            return
        
        dialog = CharacterDialog(self.current_project.id, parent=self)
        if dialog.exec():
            # Refresh the list and emit update signal
            self._refresh_characters()
            self.character_updated.emit()
