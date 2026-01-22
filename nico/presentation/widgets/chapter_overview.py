"""Chapter overview widget - landing page for chapter selection."""
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
    QToolButton,
)

from nico.domain.models import Chapter


class ChapterOverview(QWidget):
    """Landing page displayed when a chapter is selected in the binder."""
    
    # Signal emitted when user wants to create a new scene
    create_scene_requested = Signal()
    # Signal emitted when user clicks on a scene
    scene_selected = Signal(int)  # scene_id
    # Signal emitted when scene order changes
    scenes_reordered = Signal(list)  # list of scene_ids in new order
    # Signal emitted when user wants continuous writing mode
    continuous_writing_requested = Signal(int)  # chapter_id
    
    def __init__(self) -> None:
        super().__init__()
        self.current_chapter: Optional[Chapter] = None
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
        self.title_label = QLabel("Chapter")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(self.title_label)
        
        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #666; font-size: 14px;")
        header.addWidget(self.description_label)
        
        layout.addLayout(header)
        
        # Statistics group
        stats_group = QGroupBox("Chapter Statistics")
        stats_layout = QGridLayout()
        
        self.scenes_stat = QLabel("0")
        self.scenes_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Scenes:"), 0, 0)
        stats_layout.addWidget(self.scenes_stat, 0, 1)
        
        self.word_count_stat = QLabel("0")
        self.word_count_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Total Words:"), 0, 2)
        stats_layout.addWidget(self.word_count_stat, 0, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Scenes index group
        scenes_group = QGroupBox("Scene Index")
        scenes_layout = QVBoxLayout()
        
        # Buttons row
        create_btn_layout = QHBoxLayout()
        self.create_scene_btn = QPushButton("➕ New Scene")
        self.create_scene_btn.clicked.connect(self.create_scene_requested.emit)
        create_btn_layout.addWidget(self.create_scene_btn)
        
        self.continuous_write_btn = QPushButton("📖 Continuous Writing Mode")
        self.continuous_write_btn.clicked.connect(self._on_continuous_writing)
        self.continuous_write_btn.setToolTip("Open all scenes in seamless writing view")
        create_btn_layout.addWidget(self.continuous_write_btn)
        
        create_btn_layout.addStretch()
        scenes_layout.addLayout(create_btn_layout)
        
        # Scenes list with reordering controls
        list_layout = QHBoxLayout()
        
        self.scenes_list = QListWidget()
        self.scenes_list.itemDoubleClicked.connect(self._on_scene_double_clicked)
        list_layout.addWidget(self.scenes_list)
        
        # Reorder buttons
        reorder_buttons = QVBoxLayout()
        self.move_up_btn = QToolButton()
        self.move_up_btn.setText("▲")
        self.move_up_btn.setToolTip("Move scene up")
        self.move_up_btn.clicked.connect(self._move_scene_up)
        reorder_buttons.addWidget(self.move_up_btn)
        
        self.move_down_btn = QToolButton()
        self.move_down_btn.setText("▼")
        self.move_down_btn.setToolTip("Move scene down")
        self.move_down_btn.clicked.connect(self._move_scene_down)
        reorder_buttons.addWidget(self.move_down_btn)
        
        reorder_buttons.addStretch()
        list_layout.addLayout(reorder_buttons)
        
        scenes_layout.addLayout(list_layout)
        
        scenes_group.setLayout(scenes_layout)
        layout.addWidget(scenes_group)
        
        layout.addStretch()
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
    def load_chapter(self, chapter: Chapter) -> None:
        """Load chapter data into the overview."""
        self.current_chapter = chapter
        
        # Update header
        self.title_label.setText(f"📑 Chapter {chapter.number}: {chapter.title}")
        self.description_label.setText(chapter.description or "No description provided")
        
        # Calculate statistics
        total_words = sum(scene.word_count for scene in chapter.scenes)
        
        # Update statistics
        self.scenes_stat.setText(str(len(chapter.scenes)))
        self.word_count_stat.setText(f"{total_words:,}")
        
        # Update scenes list
        self.scenes_list.clear()
        for scene in chapter.scenes:
            item = QListWidgetItem(
                f"✍️ {scene.title}\n"
                f"   {scene.word_count:,} words"
                + (f" • {scene.beat}" if scene.beat else "")
            )
            item.setData(Qt.ItemDataRole.UserRole, scene.id)
            self.scenes_list.addItem(item)
    
    def _on_scene_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on a scene."""
        scene_id = item.data(Qt.ItemDataRole.UserRole)
        if scene_id:
            self.scene_selected.emit(scene_id)
    
    def _on_continuous_writing(self) -> None:
        """Handle continuous writing mode button."""
        if self.current_chapter:
            self.continuous_writing_requested.emit(self.current_chapter.id)
    
    def _move_scene_up(self) -> None:
        """Move selected scene up in the list."""
        current_row = self.scenes_list.currentRow()
        if current_row > 0:
            item = self.scenes_list.takeItem(current_row)
            self.scenes_list.insertItem(current_row - 1, item)
            self.scenes_list.setCurrentRow(current_row - 1)
            self._emit_reordered()
    
    def _move_scene_down(self) -> None:
        """Move selected scene down in the list."""
        current_row = self.scenes_list.currentRow()
        if current_row < self.scenes_list.count() - 1:
            item = self.scenes_list.takeItem(current_row)
            self.scenes_list.insertItem(current_row + 1, item)
            self.scenes_list.setCurrentRow(current_row + 1)
            self._emit_reordered()
    
    def _emit_reordered(self) -> None:
        """Emit signal with new scene order."""
        scene_ids = []
        for i in range(self.scenes_list.count()):
            item = self.scenes_list.item(i)
            scene_id = item.data(Qt.ItemDataRole.UserRole)
            if scene_id:
                scene_ids.append(scene_id)
        self.scenes_reordered.emit(scene_ids)
