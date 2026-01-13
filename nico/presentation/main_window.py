"""Main window for Nico application."""
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QLabel,
    QStatusBar,
    QMenuBar,
)

from nico.presentation.widgets.binder import BinderWidget
from nico.presentation.widgets.editor import EditorWidget
from nico.presentation.widgets.inspector import InspectorWidget


class MainWindow(QMainWindow):
    """Main application window with Scrivener-like layout."""
    
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Nico - Narrative Insight Composition Output")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create UI components
        self._setup_menubar()
        self._setup_central_widget()
        self._setup_statusbar()
        
    def _setup_menubar(self) -> None:
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&New Project...", self._on_new_project)
        file_menu.addAction("&Open Project...", self._on_open_project)
        file_menu.addSeparator()
        file_menu.addAction("&Save", self._on_save)
        file_menu.addAction("Save &As...", self._on_save_as)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction("&Undo")
        edit_menu.addAction("&Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Cu&t")
        edit_menu.addAction("&Copy")
        edit_menu.addAction("&Paste")
        
        # Project menu
        project_menu = menubar.addMenu("&Project")
        project_menu.addAction("New &Story...")
        project_menu.addAction("New &Chapter...")
        project_menu.addAction("New &Scene...")
        project_menu.addSeparator()
        project_menu.addAction("Project &Settings...")
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction("&Characters...")
        tools_menu.addAction("&Locations...")
        tools_menu.addAction("&Events/Timeline...")
        tools_menu.addSeparator()
        tools_menu.addAction("&Word Count Statistics...")
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("&About Nico")
        help_menu.addAction("&Documentation")
        
    def _setup_central_widget(self) -> None:
        """Create the central widget with three-panel layout."""
        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Binder (project tree)
        self.binder = BinderWidget()
        main_splitter.addWidget(self.binder)
        
        # Center panel: Editor
        self.editor = EditorWidget()
        main_splitter.addWidget(self.editor)
        
        # Right panel: Inspector
        self.inspector = InspectorWidget()
        main_splitter.addWidget(self.inspector)
        
        # Set initial sizes (20%, 50%, 30%)
        main_splitter.setSizes([280, 700, 420])
        
        self.setCentralWidget(main_splitter)
        
    def _setup_statusbar(self) -> None:
        """Create the status bar."""
        status_bar = QStatusBar()
        status_bar.showMessage("Ready")
        self.setStatusBar(status_bar)
        
    # Menu action handlers (placeholders)
    def _on_new_project(self) -> None:
        """Handle New Project action."""
        self.statusBar().showMessage("New Project (not implemented)")
        
    def _on_open_project(self) -> None:
        """Handle Open Project action."""
        self.statusBar().showMessage("Open Project (not implemented)")
        
    def _on_save(self) -> None:
        """Handle Save action."""
        self.statusBar().showMessage("Save (not implemented)")
        
    def _on_save_as(self) -> None:
        """Handle Save As action."""
        self.statusBar().showMessage("Save As (not implemented)")
