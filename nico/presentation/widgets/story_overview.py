"""Story overview widget - landing page for story selection."""
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

from nico.domain.models import Story


class StoryOverview(QWidget):
    """Landing page displayed when a story is selected in the binder."""
    
    # Signal emitted when user wants to create a new chapter
    create_chapter_requested = Signal()
    # Signal emitted when user clicks on a chapter
    chapter_selected = Signal(int)  # chapter_id
    # Signal emitted when chapter order changes
    chapters_reordered = Signal(list)  # list of chapter_ids in new order
    
    def __init__(self) -> None:
        super().__init__()
        self.current_story: Optional[Story] = None
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
        self.title_label = QLabel("Story")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(self.title_label)
        
        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #666; font-size: 14px;")
        header.addWidget(self.description_label)
        
        layout.addLayout(header)
        
        # Statistics group
        stats_group = QGroupBox("Story Statistics")
        stats_layout = QGridLayout()
        
        self.chapters_stat = QLabel("0")
        self.chapters_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Chapters:"), 0, 0)
        stats_layout.addWidget(self.chapters_stat, 0, 1)
        
        self.scenes_stat = QLabel("0")
        self.scenes_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Scenes:"), 0, 2)
        stats_layout.addWidget(self.scenes_stat, 0, 3)
        
        self.word_count_stat = QLabel("0")
        self.word_count_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Total Words:"), 1, 0)
        stats_layout.addWidget(self.word_count_stat, 1, 1)
        
        self.target_words_stat = QLabel("Not set")
        self.target_words_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Target Words:"), 1, 2)
        stats_layout.addWidget(self.target_words_stat, 1, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Chapters index group
        chapters_group = QGroupBox("Chapter Index")
        chapters_layout = QVBoxLayout()
        
        # Create chapter button
        create_btn_layout = QHBoxLayout()
        self.create_chapter_btn = QPushButton("➕ New Chapter")
        self.create_chapter_btn.clicked.connect(self.create_chapter_requested.emit)
        create_btn_layout.addWidget(self.create_chapter_btn)
        create_btn_layout.addStretch()
        chapters_layout.addLayout(create_btn_layout)
        
        # Chapters list with reordering controls
        list_layout = QHBoxLayout()
        
        self.chapters_list = QListWidget()
        self.chapters_list.itemDoubleClicked.connect(self._on_chapter_double_clicked)
        list_layout.addWidget(self.chapters_list)
        
        # Reorder buttons
        reorder_buttons = QVBoxLayout()
        self.move_up_btn = QToolButton()
        self.move_up_btn.setText("▲")
        self.move_up_btn.setToolTip("Move chapter up")
        self.move_up_btn.clicked.connect(self._move_chapter_up)
        reorder_buttons.addWidget(self.move_up_btn)
        
        self.move_down_btn = QToolButton()
        self.move_down_btn.setText("▼")
        self.move_down_btn.setToolTip("Move chapter down")
        self.move_down_btn.clicked.connect(self._move_chapter_down)
        reorder_buttons.addWidget(self.move_down_btn)
        
        reorder_buttons.addStretch()
        list_layout.addLayout(reorder_buttons)
        
        chapters_layout.addLayout(list_layout)
        
        chapters_group.setLayout(chapters_layout)
        layout.addWidget(chapters_group)
        
        layout.addStretch()
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
    def load_story(self, story: Story) -> None:
        """Load story data into the overview."""
        self.current_story = story
        
        # Update header
        self.title_label.setText(f"📖 {story.title}")
        self.description_label.setText(story.description or "No description provided")
        
        # Calculate statistics
        total_scenes = sum(len(chapter.scenes) for chapter in story.chapters)
        total_words = sum(
            scene.word_count
            for chapter in story.chapters
            for scene in chapter.scenes
        )
        
        # Update statistics
        self.chapters_stat.setText(str(len(story.chapters)))
        self.scenes_stat.setText(str(total_scenes))
        self.word_count_stat.setText(f"{total_words:,}")
        
        # TODO: Update when target_word_count is added to Story model
        self.target_words_stat.setText("Not set")
        
        # Update chapters list
        self.chapters_list.clear()
        for chapter in story.chapters:
            scene_count = len(chapter.scenes)
            word_count = sum(scene.word_count for scene in chapter.scenes)
            
            item = QListWidgetItem(
                f"📑 Chapter {chapter.number}: {chapter.title}\n"
                f"   {scene_count} scenes, {word_count:,} words"
            )
            item.setData(Qt.ItemDataRole.UserRole, chapter.id)
            self.chapters_list.addItem(item)
    
    def _on_chapter_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on a chapter."""
        chapter_id = item.data(Qt.ItemDataRole.UserRole)
        if chapter_id:
            self.chapter_selected.emit(chapter_id)
    
    def _move_chapter_up(self) -> None:
        """Move selected chapter up in the list."""
        current_row = self.chapters_list.currentRow()
        if current_row > 0:
            item = self.chapters_list.takeItem(current_row)
            self.chapters_list.insertItem(current_row - 1, item)
            self.chapters_list.setCurrentRow(current_row - 1)
            self._emit_reordered()
    
    def _move_chapter_down(self) -> None:
        """Move selected chapter down in the list."""
        current_row = self.chapters_list.currentRow()
        if current_row < self.chapters_list.count() - 1:
            item = self.chapters_list.takeItem(current_row)
            self.chapters_list.insertItem(current_row + 1, item)
            self.chapters_list.setCurrentRow(current_row + 1)
            self._emit_reordered()
    
    def _emit_reordered(self) -> None:
        """Emit signal with new chapter order."""
        chapter_ids = []
        for i in range(self.chapters_list.count()):
            item = self.chapters_list.item(i)
            chapter_id = item.data(Qt.ItemDataRole.UserRole)
            if chapter_id:
                chapter_ids.append(chapter_id)
        self.chapters_reordered.emit(chapter_ids)
