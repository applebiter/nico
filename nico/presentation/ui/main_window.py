"""Main application window."""

from pathlib import Path
from typing import Optional
from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QTreeWidgetItemIterator,
    QVBoxLayout,
    QWidget,
)

from nico.application.use_cases import (
    CreateChapterUseCase,
    CreateProjectUseCase,
    CreateSceneUseCase,
    CreateStoryUseCase,
    GetSceneUseCase,
    ListChaptersUseCase,
    ListScenesUseCase,
    ListStoriesUseCase,
    OpenProjectUseCase,
    UpdateSceneDocumentUseCase,
)
from nico.domain.models import Project
from nico.infrastructure.persistence import (
    ChapterRepository,
    Database,
    ProjectRepository,
    SceneDocumentRepository,
    SceneRepository,
    StoryRepository,
)
from nico.presentation.ui.binder_tree import BinderTreeWidget
from nico.presentation.ui.new_project_dialog import NewProjectDialog
from nico.presentation.ui.scene_editor import SceneEditor


class MainWindow(QMainWindow):
    """Main application window with binder, editor, and inspector."""

    def __init__(self) -> None:
        super().__init__()
        self.current_project: Optional[Project] = None
        self.database: Optional[Database] = None
        self._init_ui()
        self._create_menus()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("nico")
        self.setGeometry(100, 100, 1400, 900)

        # Main splitter layout: binder | editor | inspector
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Binder (left panel)
        self.binder_widget = QWidget()
        binder_layout = QVBoxLayout(self.binder_widget)
        binder_layout.setContentsMargins(0, 0, 0, 0)
        
        self.binder_tree = BinderTreeWidget()
        self.binder_tree.item_selected.connect(self._on_binder_item_selected)
        self.binder_tree.item_double_clicked.connect(self._on_binder_item_double_clicked)
        self.binder_tree.add_story_requested.connect(self._on_add_story)
        self.binder_tree.add_chapter_requested.connect(self._on_add_chapter)
        self.binder_tree.add_scene_requested.connect(self._on_add_scene)
        self.binder_tree.delete_item_requested.connect(self._on_delete_item)
        binder_layout.addWidget(self.binder_tree)

        # Editor (center panel)
        self.scene_editor = SceneEditor()
        self.scene_editor.content_changed.connect(self._on_scene_content_changed)

        # Inspector (right panel)
        self.inspector_widget = QWidget()
        inspector_layout = QVBoxLayout(self.inspector_widget)
        inspector_layout.setContentsMargins(10, 10, 10, 10)
        
        self.inspector_label = QLabel("Inspector")
        inspector_layout.addWidget(self.inspector_label)

        # Add panels to splitter
        main_splitter.addWidget(self.binder_widget)
        main_splitter.addWidget(self.scene_editor)
        main_splitter.addWidget(self.inspector_widget)

        # Set initial sizes: binder 20%, editor 50%, inspector 30%
        main_splitter.setSizes([280, 700, 420])

        # Set as central widget
        self.setCentralWidget(main_splitter)

    def _create_menus(self) -> None:
        """Create application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_project_action = file_menu.addAction("&New Project...")
        new_project_action.setShortcut("Ctrl+Shift+N")
        new_project_action.triggered.connect(self._on_new_project)

        open_project_action = file_menu.addAction("&Open Project...")
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.triggered.connect(self._on_open_project)

        file_menu.addSeparator()

        close_project_action = file_menu.addAction("&Close Project")
        close_project_action.triggered.connect(self._on_close_project)

        file_menu.addSeparator()

        quit_action = file_menu.addAction("&Quit")
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        # TODO: Add edit actions

        # View menu
        view_menu = menubar.addMenu("&View")
        # TODO: Add view actions

        # Project menu
        project_menu = menubar.addMenu("&Project")
        # TODO: Add project actions

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = help_menu.addAction("&About nico")
        about_action.triggered.connect(self._on_about)

    def _on_new_project(self) -> None:
        """Handle new project creation."""
        dialog = NewProjectDialog(self)
        if dialog.exec():
            data = dialog.get_project_data()
            try:
                # Create full project path
                project_path = data["path"] / data["name"]
                
                # Initialize database for this project
                db_path = project_path / "project.sqlite3"
                self.database = Database(db_path)
                self.database.create_tables()
                
                # Create repositories
                session = next(self.database.get_session())
                project_repo = ProjectRepository(session)
                
                # Create project using use case
                create_project = CreateProjectUseCase(project_repo, self.database)
                self.current_project = create_project.execute(
                    name=data["name"],
                    path=project_path,
                    description=data["description"],
                    author=data["author"],
                    local_only_ai=data["local_only_ai"],
                )
                
                # Update UI
                self._load_project()
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Project '{data['name']}' created successfully!",
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create project:\n{str(e)}")

    def _on_open_project(self) -> None:
        """Handle opening an existing project."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Open Project Folder",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly,
        )
        
        if folder:
            try:
                project_path = Path(folder)
                db_path = project_path / "project.sqlite3"
                
                if not db_path.exists():
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"No project found at:\n{folder}\n\nMake sure you're opening a nico project folder.",
                    )
                    return
                
                # Initialize database
                self.database = Database(db_path)
                
                # Open project using use case
                session = next(self.database.get_session())
                project_repo = ProjectRepository(session)
                
                open_project = OpenProjectUseCase(project_repo)
                self.current_project = open_project.execute(project_path)
                
                # Update UI
                self._load_project()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open project:\n{str(e)}")

    def _on_close_project(self) -> None:
        """Handle closing the current project."""
        if self.current_project:
            # Save any unsaved changes
            self.scene_editor.save_now()
            
            self.current_project = None
            self.database = None
            self.binder_tree.clear_project()
            self.scene_editor.clear()
            self.setWindowTitle("nico")

    def _load_project(self) -> None:
        """Load project data into the UI."""
        if not self.current_project or not self.database:
            return
        
        # Update window title
        self.setWindowTitle(f"{self.current_project.name} - nico")
        
        # Clear binder and set project
        self.binder_tree.set_project(self.current_project.name)
        
        # Load stories
        try:
            session = next(self.database.get_session())
            story_repo = StoryRepository(session)
            chapter_repo = ChapterRepository(session)
            scene_repo = SceneRepository(session)
            
            list_stories = ListStoriesUseCase(story_repo)
            stories = list_stories.execute(self.current_project.id)
            
            # Add stories to binder
            for story in stories:
                story_item = self.binder_tree.add_story(story.id, story.title)
                
                # Load chapters for this story
                list_chapters = ListChaptersUseCase(chapter_repo)
                chapters = list_chapters.execute(story.id)
                for chapter in chapters:
                    chapter_item = self.binder_tree.add_chapter(story_item, chapter.id, chapter.title)
                    
                    # Load scenes for this chapter
                    list_scenes = ListScenesUseCase(scene_repo)
                    scenes = list_scenes.execute(chapter.id)
                    for scene in scenes:
                        self.binder_tree.add_scene(chapter_item, scene.id, scene.title)
            
            # Clear editor
            self.scene_editor.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load project:\n{str(e)}")

    def _on_binder_item_selected(self, item_type: str, item_id: UUID) -> None:
        """Handle binder item selection."""
        # Update inspector with metadata (TODO: implement inspector)
        pass

    def _on_binder_item_double_clicked(self, item_type: str, item_id: UUID) -> None:
        """Handle binder item double-click."""
        if item_type == "scene":
            self._load_scene(item_id)

    def _load_scene(self, scene_id: UUID) -> None:
        """Load a scene into the editor."""
        if not self.database:
            return
        
        try:
            session = next(self.database.get_session())
            scene_repo = SceneRepository(session)
            
            get_scene = GetSceneUseCase(scene_repo)
            scene = get_scene.execute(scene_id)
            
            if scene and scene.document:
                self.scene_editor.load_scene(
                    scene.id,
                    scene.title,
                    scene.document.content
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load scene:\n{str(e)}")

    def _on_scene_content_changed(self, scene_id: UUID, content_json: str) -> None:
        """Handle scene content changes (autosave)."""
        if not self.database:
            return
        
        try:
            session = next(self.database.get_session())
            scene_repo = SceneRepository(session)
            scene_doc_repo = SceneDocumentRepository(session)
            
            update_doc = UpdateSceneDocumentUseCase(scene_repo, scene_doc_repo)
            update_doc.execute(
                scene_id=scene_id,
                content=content_json,
                create_revision=False  # Only create revisions on manual save
            )
        except Exception as e:
            # Log error but don't interrupt user's workflow
            print(f"Autosave error: {e}")

    def _on_add_story(self) -> None:
        """Handle adding a new story."""
        if not self.current_project or not self.database:
            QMessageBox.warning(self, "No Project", "Please open a project first")
            return
        
        title, ok = QInputDialog.getText(self, "New Story", "Story title:")
        if ok and title:
            try:
                session = next(self.database.get_session())
                story_repo = StoryRepository(session)
                
                create_story = CreateStoryUseCase(story_repo)
                story = create_story.execute(
                    project_id=self.current_project.id,
                    title=title,
                )
                
                # Add to binder
                self.binder_tree.add_story(story.id, story.title)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create story:\n{str(e)}")

    def _on_add_chapter(self, story_id: UUID) -> None:
        """Handle adding a new chapter."""
        if not self.current_project or not self.database:
            return
        
        title, ok = QInputDialog.getText(self, "New Chapter", "Chapter title:")
        if ok and title:
            try:
                session = next(self.database.get_session())
                chapter_repo = ChapterRepository(session)
                
                create_chapter = CreateChapterUseCase(chapter_repo)
                chapter = create_chapter.execute(
                    story_id=story_id,
                    title=title,
                )
                
                # Find the story item in the tree and add chapter
                story_item = self._find_tree_item("story", story_id)
                if story_item:
                    self.binder_tree.add_chapter(story_item, chapter.id, chapter.title)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create chapter:\n{str(e)}")

    def _on_add_scene(self, chapter_id: UUID) -> None:
        """Handle adding a new scene."""
        if not self.current_project or not self.database:
            return
        
        title, ok = QInputDialog.getText(self, "New Scene", "Scene title:")
        if ok and title:
            try:
                session = next(self.database.get_session())
                scene_repo = SceneRepository(session)
                
                create_scene = CreateSceneUseCase(scene_repo)
                scene = create_scene.execute(
                    chapter_id=chapter_id,
                    title=title,
                )
                
                # Find the chapter item in the tree and add scene
                chapter_item = self._find_tree_item("chapter", chapter_id)
                if chapter_item:
                    self.binder_tree.add_scene(chapter_item, scene.id, scene.title)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create scene:\n{str(e)}")

    def _on_delete_item(self, item_type: str, item_id: UUID) -> None:
        """Handle deleting an item."""
        # TODO: Implement delete functionality with use cases
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this {item_type}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Delete", f"Delete {item_type} functionality coming soon!")

    def _find_tree_item(self, item_type: str, item_id: UUID):
        """Find a tree item by type and ID."""
        from nico.presentation.ui.binder_tree import BinderItem
        
        iterator = QTreeWidgetItemIterator(self.binder_tree)
        while iterator.value():
            item = iterator.value()
            if isinstance(item, BinderItem):
                if item.item_type == item_type and item.item_id == item_id:
                    return item
            iterator += 1
        return None

    def _on_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About nico",
            "<h2>nico</h2>"
            "<p>Narrative Insight Composition Output</p>"
            "<p>A local-first writing application for long-form fiction.</p>"
            "<p>Version 0.1.0</p>"
            "<p>Licensed under MIT License</p>",
        )
