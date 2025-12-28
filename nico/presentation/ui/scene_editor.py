"""Scene editor widget for editing scene content."""

import json
from typing import Optional
from uuid import UUID

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SceneEditor(QWidget):
    """Editor widget for scene content with autosave."""

    # Signals
    content_changed = Signal(UUID, str)  # (scene_id, content_json)
    
    def __init__(self, parent: Optional[object] = None):
        super().__init__(parent)
        self.current_scene_id: Optional[UUID] = None
        self.current_scene_title: Optional[str] = None
        self._content_modified = False
        self._init_ui()
        self._init_autosave()

    def _init_ui(self) -> None:
        """Initialize the editor UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Welcome message (shown when no scene is loaded)
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_widget)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        welcome_label = QLabel(
            "<h2>Welcome to nico</h2>"
            "<p style='color: #666;'>Create a new project or open an existing one to get started.</p>"
            "<p style='color: #666; margin-top: 20px;'>"
            "<b>File → New Project</b> to create a new writing project<br>"
            "<b>File → Open Project</b> to open an existing project<br>"
            "<b>File → Open Recent</b> to quickly reopen recent work"
            "</p>"
        )
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setWordWrap(True)
        welcome_layout.addWidget(welcome_label)
        
        # Editor container
        self.editor_widget = QWidget()
        editor_layout = QVBoxLayout(self.editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(10)
        
        # Title label
        self.title_label = QLabel("No scene selected")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        editor_layout.addWidget(self.title_label)
        
        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Start writing...")
        
        # Set up editor font
        editor_font = QFont("Serif")
        editor_font.setPointSize(12)
        self.text_edit.setFont(editor_font)
        
        # Add padding around text
        self.text_edit.setStyleSheet("""
            QTextEdit {
                padding: 20px;
            }
        """)
        
        # Connect text changes
        self.text_edit.textChanged.connect(self._on_text_changed)
        
        editor_layout.addWidget(self.text_edit)
        
        # Status label for autosave
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-size: 10pt;")
        editor_layout.addWidget(self.status_label)
        
        # Add both widgets to main layout
        layout.addWidget(self.welcome_widget)
        layout.addWidget(self.editor_widget)
        
        # Show welcome by default
        self._show_welcome()

    def _show_welcome(self) -> None:
        """Show welcome screen and hide editor."""
        self.welcome_widget.show()
        self.editor_widget.hide()
    
    def _show_editor(self) -> None:
        """Show editor and hide welcome screen."""
        self.welcome_widget.hide()
        self.editor_widget.show()
    
    def _init_autosave(self) -> None:
        """Initialize autosave timer."""
        self._autosave_timer = QTimer(self)
        self._autosave_timer.timeout.connect(self._trigger_autosave)
        self._autosave_timer.setSingleShot(True)

    def load_scene(self, scene_id: UUID, title: str, content_json: str) -> None:
        """Load a scene into the editor."""
        self.current_scene_id = scene_id
        self.current_scene_title = title
        self._content_modified = False
        
        # Show editor instead of welcome
        self._show_editor()
        
        # Update title
        self.title_label.setText(title)
        
        # Parse content from ProseMirror JSON
        try:
            # Handle both JSON string and dict
            if isinstance(content_json, str):
                content_data = json.loads(content_json) if content_json else {"type": "doc", "content": []}
            else:
                content_data = content_json
            
            # Extract text content from ProseMirror structure
            text = self._extract_text_from_prosemirror(content_data)
            
            # Block signals while setting content to avoid triggering autosave
            self.text_edit.blockSignals(True)
            self.text_edit.setPlainText(text)
            self.text_edit.blockSignals(False)
            
            # Move cursor to start
            cursor = self.text_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.text_edit.setTextCursor(cursor)
            
            self.status_label.setText("Loaded")
            
        except Exception as e:
            self.status_label.setText(f"Error loading: {str(e)}")

    def _extract_text_from_prosemirror(self, doc: dict) -> str:
        """Extract plain text from ProseMirror document structure."""
        if not doc or "content" not in doc:
            return ""
        
        text_parts = []
        for node in doc.get("content", []):
            if node.get("type") == "paragraph":
                paragraph_text = []
                for content_node in node.get("content", []):
                    if content_node.get("type") == "text":
                        paragraph_text.append(content_node.get("text", ""))
                text_parts.append("".join(paragraph_text))
        
        return "\n\n".join(text_parts)

    def _convert_to_prosemirror(self, text: str) -> str:
        """Convert plain text to ProseMirror JSON format."""
        # Split into paragraphs
        paragraphs = text.split("\n\n") if text else [""]
        
        content = []
        for para_text in paragraphs:
            if para_text.strip():
                content.append({
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": para_text
                        }
                    ]
                })
            else:
                # Empty paragraph
                content.append({
                    "type": "paragraph"
                })
        
        doc = {
            "type": "doc",
            "content": content
        }
        
        return json.dumps(doc)

    def _on_text_changed(self) -> None:
        """Handle text changes."""
        if self.current_scene_id is None:
            return
        
        self._content_modified = True
        self.status_label.setText("Modified...")
        
        # Restart autosave timer (2 seconds after last keystroke)
        self._autosave_timer.stop()
        self._autosave_timer.start(2000)

    def _trigger_autosave(self) -> None:
        """Trigger autosave."""
        if not self._content_modified or self.current_scene_id is None:
            return
        
        # Convert current text to ProseMirror JSON
        text = self.text_edit.toPlainText()
        content_json = self._convert_to_prosemirror(text)
        
        # Emit signal for main window to handle saving
        self.content_changed.emit(self.current_scene_id, content_json)
        
        self._content_modified = False
        self.status_label.setText("Saved")

    def clear(self) -> None:
        """Clear the editor."""
        self.current_scene_id = None
        self.current_scene_title = None
        self._content_modified = False
        self._autosave_timer.stop()
        
        self.title_label.setText("No scene selected")
        self.text_edit.blockSignals(True)
        self.text_edit.clear()
        self.text_edit.blockSignals(False)
        self.status_label.setText("")
        
        # Show welcome screen
        self._show_welcome()

    def save_now(self) -> None:
        """Force immediate save."""
        self._autosave_timer.stop()
        self._trigger_autosave()
