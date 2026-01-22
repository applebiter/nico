"""Stories overview widget - listing page for all stories in a project."""
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
    QGridLayout,
)

from nico.domain.models import Project
from nico.application.context import get_app_context
from nico.presentation.widgets.story_dialog import StoryDialog


class StoriesOverview(QWidget):
    """Landing page displayed when Stories collection is selected in the binder."""
    
    # Signal emitted when user wants to create a new story
    create_story_requested = Signal()
    # Signal emitted when user clicks on a story
    story_selected = Signal(int)  # story_id
    # Signal emitted when a story is created/updated
    story_updated = Signal()
    
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
        self.title_label = QLabel("📚 Stories")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(self.title_label)
        
        self.description_label = QLabel("Manage the stories in your project")
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
        stats_layout.addWidget(QLabel("Total Chapters:"), 0, 2)
        stats_layout.addWidget(self.chapters_stat, 0, 3)
        
        self.scenes_stat = QLabel("0")
        self.scenes_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Total Scenes:"), 0, 4)
        stats_layout.addWidget(self.scenes_stat, 0, 5)
        
        self.word_count_stat = QLabel("0")
        self.word_count_stat.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(QLabel("Total Words:"), 1, 0)
        stats_layout.addWidget(self.word_count_stat, 1, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Stories list group
        stories_group = QGroupBox("All Stories")
        stories_layout = QVBoxLayout()
        
        # Create story button
        create_btn_layout = QHBoxLayout()
        self.create_story_btn = QPushButton("➕ New Story")
        self.create_story_btn.clicked.connect(self._on_create_story)
        create_btn_layout.addWidget(self.create_story_btn)
        create_btn_layout.addStretch()
        stories_layout.addLayout(create_btn_layout)
        
        # Story list
        self.stories_list = QListWidget()
        self.stories_list.setMinimumHeight(300)
        self.stories_list.itemDoubleClicked.connect(self._on_story_double_clicked)
        stories_layout.addWidget(self.stories_list)
        
        stories_group.setLayout(stories_layout)
        layout.addWidget(stories_group)
        
        layout.addStretch()
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        # Set scroll area as the main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
    def load_project(self, project: Project) -> None:
        """Load stories for a project."""
        self.current_project = project
        self._refresh_stories()
        self._update_stats()
        
    def _refresh_stories(self) -> None:
        """Refresh the stories list."""
        self.stories_list.clear()
        
        if not self.current_project:
            return
        
        # Get all stories
        stories = self.current_project.stories
        
        if not stories:
            item = QListWidgetItem("No stories yet. Create one to get started!")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.stories_list.addItem(item)
            return
        
        # Add stories to list
        for story in stories:
            chapter_count = len(story.chapters)
            scene_count = sum(len(chapter.scenes) for chapter in story.chapters)
            word_count = sum(
                sum(scene.word_count or 0 for scene in chapter.scenes)
                for chapter in story.chapters
            )
            
            display_text = f"📖 {story.title}"
            subtitle = f"   {chapter_count} chapter{'s' if chapter_count != 1 else ''}, "
            subtitle += f"{scene_count} scene{'s' if scene_count != 1 else ''}, "
            subtitle += f"{word_count:,} words"
            
            if story.description:
                display_text += f"\n{subtitle}\n   {story.description[:80]}{'...' if len(story.description) > 80 else ''}"
            else:
                display_text += f"\n{subtitle}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, story.id)
            self.stories_list.addItem(item)
    
    def _update_stats(self) -> None:
        """Update the statistics display."""
        if not self.current_project:
            return
        
        stories = self.current_project.stories
        total_chapters = sum(len(story.chapters) for story in stories)
        total_scenes = sum(
            sum(len(chapter.scenes) for chapter in story.chapters)
            for story in stories
        )
        total_words = sum(
            sum(
                sum(scene.word_count or 0 for scene in chapter.scenes)
                for chapter in story.chapters
            )
            for story in stories
        )
        
        self.stories_stat.setText(str(len(stories)))
        self.chapters_stat.setText(str(total_chapters))
        self.scenes_stat.setText(str(total_scenes))
        self.word_count_stat.setText(f"{total_words:,}")
    
    def _on_story_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on story item."""
        story_id = item.data(Qt.ItemDataRole.UserRole)
        if story_id:
            self.story_selected.emit(story_id)
    
    def _on_create_story(self) -> None:
        """Handle create story request."""
        if not self.current_project:
            return
        
        dialog = StoryDialog(self.current_project.id, parent=self)
        if dialog.exec():
            # Refresh the list and emit update signal
            self.load_project(self.current_project)
            self.story_updated.emit()
