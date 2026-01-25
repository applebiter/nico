"""Scene editor widget - WYSIWYG editor for scene content using TipTap."""
import os
from typing import Optional

from PySide6.QtCore import Qt, Signal, QObject, Slot, QUrl
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QToolBar,
    QPushButton,
    QMessageBox,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

from nico.domain.models import Scene
from nico.application.context import get_app_context


class EditorBridge(QObject):
    """Bridge object for communication between Python and JavaScript."""
    
    contentChangedSignal = Signal(str, str, int)  # html, json, word_count
    editorReadySignal = Signal()
    
    @Slot(str, str, int)
    def contentChanged(self, html: str, json: str, word_count: int):
        """Called by JavaScript when content changes."""
        self.contentChangedSignal.emit(html, json, word_count)
    
    @Slot()
    def editorReady(self):
        """Called by JavaScript when editor is initialized."""
        self.editorReadySignal.emit()


class SceneEditor(QWidget):
    """WYSIWYG editor for scene content using TipTap in a web view."""
    
    # Signal emitted when scene is updated (edited/deleted)
    scene_updated = Signal()
    
    def __init__(self) -> None:
        super().__init__()
        self.current_scene: Optional[Scene] = None
        self.app_context = get_app_context()
        self.auto_save_enabled = True
        self._content_dirty = False
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header with scene info
        header = QHBoxLayout()
        header.setSpacing(8)
        self.scene_title = QLabel("No scene selected")
        self.scene_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(self.scene_title)
        
        header.addStretch()
        
        self.delete_btn = QPushButton("🗑️ Delete Scene")
        self.delete_btn.clicked.connect(self._on_delete_scene)
        self.delete_btn.setVisible(False)  # Hidden until scene is loaded
        header.addWidget(self.delete_btn)
        
        self.word_count = QLabel("0 words")
        self.word_count.setStyleSheet("color: #666;")
        header.addWidget(self.word_count)
        
        layout.addLayout(header)
        
        # Formatting toolbar
        toolbar = QToolBar()
        toolbar.setStyleSheet("QToolBar { border: none; spacing: 5px; padding: 2px; }")
        toolbar.setMaximumHeight(32)
        
        bold_action = toolbar.addAction("B")
        bold_action.setToolTip("Bold")
        bold_action.triggered.connect(self._on_bold)
        
        italic_action = toolbar.addAction("I")
        italic_action.setToolTip("Italic")
        italic_action.triggered.connect(self._on_italic)
        
        underline_action = toolbar.addAction("U")
        underline_action.setToolTip("Underline")
        underline_action.triggered.connect(self._on_underline)
        
        toolbar.addSeparator()
        
        h1_action = toolbar.addAction("H1")
        h1_action.setToolTip("Heading 1")
        h1_action.triggered.connect(lambda: self._on_heading(1))
        
        h2_action = toolbar.addAction("H2")
        h2_action.setToolTip("Heading 2")
        h2_action.triggered.connect(lambda: self._on_heading(2))
        
        h3_action = toolbar.addAction("H3")
        h3_action.setToolTip("Heading 3")
        h3_action.triggered.connect(lambda: self._on_heading(3))
        
        toolbar.addSeparator()
        
        bullet_action = toolbar.addAction("• List")
        bullet_action.setToolTip("Bullet List")
        bullet_action.triggered.connect(self._on_bullet_list)
        
        number_action = toolbar.addAction("1. List")
        number_action.setToolTip("Numbered List")
        number_action.triggered.connect(self._on_numbered_list)
        
        quote_action = toolbar.addAction("\" Quote")
        quote_action.setToolTip("Block Quote")
        quote_action.triggered.connect(self._on_blockquote)
        
        layout.addWidget(toolbar)
        
        # Web view with TipTap editor
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(400)
        
        # Enable developer tools for debugging
        from PySide6.QtWebEngineCore import QWebEngineSettings
        settings = self.web_view.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        
        # Set up QWebChannel for Python-JavaScript communication
        self.channel = QWebChannel()
        self.bridge = EditorBridge()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        
        # Connect signals
        self.bridge.contentChangedSignal.connect(self._on_content_changed)
        self.bridge.editorReadySignal.connect(self._on_editor_ready)
        
        # Enable console logging
        self.web_view.page().javaScriptConsoleMessage = self._on_js_console_message
        
        # Load the editor HTML
        editor_html_path = os.path.join(
            os.path.dirname(__file__), 
            "editor_template.html"
        )
        print(f"Loading editor from: {editor_html_path}")
        self.web_view.setUrl(QUrl.fromLocalFile(editor_html_path))
        
        layout.addWidget(self.web_view, 1)  # Stretch factor of 1 to expand
        
        # Footer with scene metadata
        self.footer = QHBoxLayout()
        self.footer.setSpacing(12)
        self.footer.setContentsMargins(0, 5, 0, 0)
        self.beat_label = QLabel("")
        self.pov_label = QLabel("")
        self.setting_label = QLabel("")
        
        self.footer.addWidget(self.beat_label)
        self.footer.addStretch()
        self.footer.addWidget(self.pov_label)
        self.footer.addWidget(self.setting_label)
        
        layout.addLayout(self.footer)
        self.setLayout(layout)
    
    def _on_js_console_message(self, level, message, line, source):
        """Log JavaScript console messages to Python console."""
        print(f"JS Console [{level}] {source}:{line} - {message}")
    
    def _on_editor_ready(self):
        """Called when the JavaScript editor is ready."""
        # Set theme
        from nico.preferences import Preferences
        prefs = Preferences()
        theme = prefs.theme
        self.web_view.page().runJavaScript(f"setTheme('{theme}');")
        
        # If we have a current scene, load it
        if self.current_scene:
            self._load_content_to_editor()
    
    def _on_content_changed(self, html: str, json: str, word_count: int):
        """Called when editor content changes."""
        self.word_count.setText(f"{word_count:,} words")
        self._content_dirty = True
        
        # Auto-save if enabled and we have a current scene
        if self.auto_save_enabled and self.current_scene:
            self._save_content(html, word_count)
    
    def _save_content(self, html: str, word_count: int):
        """Save content to the database."""
        if not self.current_scene:
            return
        
        try:
            self.current_scene.content = html
            self.current_scene.word_count = word_count
            self.app_context.commit()
            self._content_dirty = False
        except Exception as e:
            self.app_context.rollback()
            print(f"Error saving scene: {e}")
    
    def load_scene(self, scene: Scene) -> None:
        """Load a scene into the editor."""
        self.current_scene = scene
        
        # Update header
        self.scene_title.setText(f"✍️ {scene.title}")
        self.word_count.setText(f"{scene.word_count:,} words")
        self.delete_btn.setVisible(True)
        
        # Load content into editor
        self._load_content_to_editor()
        
        # Update footer
        self.beat_label.setText(f"Beat: {scene.beat}" if scene.beat else "")
        
        if scene.meta:
            pov = scene.meta.get('pov', '')
            setting = scene.meta.get('setting', '')
            self.pov_label.setText(f"POV: {pov}" if pov else "")
            self.setting_label.setText(f"Setting: {setting}" if setting else "")
        else:
            self.pov_label.setText("")
            self.setting_label.setText("")
    
    def _load_content_to_editor(self):
        """Load current scene content into the JavaScript editor."""
        if not self.current_scene:
            return
        
        # Set theme
        from nico.preferences import Preferences
        prefs = Preferences()
        theme = prefs.theme
        self.web_view.page().runJavaScript(f"setTheme('{theme}');")
        
        content = self.current_scene.content or ""
        # Escape content for JavaScript
        content_escaped = content.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')
        js = f"setContent('{content_escaped}');"
        self.web_view.page().runJavaScript(js)
    
    # Formatting action handlers
    def _on_bold(self) -> None:
        """Toggle bold formatting."""
        self.web_view.page().runJavaScript("toggleBold();")
        
    def _on_italic(self) -> None:
        """Toggle italic formatting."""
        self.web_view.page().runJavaScript("toggleItalic();")
        
    def _on_underline(self) -> None:
        """Toggle underline formatting."""
        self.web_view.page().runJavaScript("toggleUnderline();")
    
    def _on_heading(self, level: int) -> None:
        """Toggle heading formatting."""
        self.web_view.page().runJavaScript(f"toggleHeading({level});")
    
    def _on_bullet_list(self) -> None:
        """Toggle bullet list."""
        self.web_view.page().runJavaScript("toggleBulletList();")
    
    def _on_numbered_list(self) -> None:
        """Toggle numbered list."""
        self.web_view.page().runJavaScript("toggleOrderedList();")
    
    def _on_blockquote(self) -> None:
        """Toggle blockquote."""
        self.web_view.page().runJavaScript("toggleBlockquote();")
    
    def _on_delete_scene(self) -> None:
        """Delete the current scene after confirmation."""
        if not self.current_scene:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Scene",
            f"Are you sure you want to delete '{self.current_scene.title}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete the scene using repository
                self.app_context.scene_service.scene_repo.delete(self.current_scene.id)
                self.app_context.commit()
                self.current_scene = None
                self.scene_title.setText("No scene selected")
                self.web_view.page().runJavaScript("setContent('');")
                self.delete_btn.setVisible(False)
                self.scene_updated.emit()
                QMessageBox.information(
                    self,
                    "Scene Deleted",
                    "The scene has been deleted."
                )
            except Exception as e:
                self.app_context.rollback()
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while deleting the scene:\n{str(e)}"
                )
