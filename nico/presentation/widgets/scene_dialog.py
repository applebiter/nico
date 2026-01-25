"""Scene creation and editing dialog."""
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QCheckBox,
    QPushButton,
    QLabel,
)

from nico.domain.models import Scene
from nico.application.context import get_app_context


class SceneDialog(QDialog):
    """Dialog for creating or editing a scene."""
    
    def __init__(self, chapter_id: int, scene: Optional[Scene] = None, parent=None):
        super().__init__(parent)
        self.chapter_id = chapter_id
        self.scene = scene
        self.is_editing = scene is not None
        self.app_context = get_app_context()
        
        self.setWindowTitle("Edit Scene" if self.is_editing else "New Scene")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self._setup_ui()
        if self.is_editing:
            self._load_scene_data()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Form layout for fields
        form = QFormLayout()
        
        # Title (required)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter scene title...")
        form.addRow("Title:*", self.title_edit)
        
        # Beat (optional)
        self.beat_edit = QLineEdit()
        self.beat_edit.setPlaceholderText("e.g., 'Opening Image', 'Midpoint', etc.")
        self.beat_edit.setToolTip("Story beat or structural note")
        form.addRow("Beat:", self.beat_edit)
        
        # Summary (optional)
        self.summary_edit = QTextEdit()
        self.summary_edit.setAcceptRichText(False)
        self.summary_edit.setPlaceholderText("Brief summary of what happens in this scene...")
        self.summary_edit.setMaximumHeight(100)
        form.addRow("Summary:", self.summary_edit)
        
        # Exclude from AI
        self.exclude_ai_checkbox = QCheckBox("Exclude this scene from AI context")
        self.exclude_ai_checkbox.setToolTip(
            "When checked, this scene's content won't be sent to AI models"
        )
        form.addRow("AI Privacy:", self.exclude_ai_checkbox)
        
        layout.addLayout(form)
        
        # Note about content
        note_label = QLabel("* Required fields\n\nNote: Scene content will be edited in the scene editor.")
        note_label.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        layout.addStretch()
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_scene)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _load_scene_data(self) -> None:
        """Load existing scene data into the form."""
        if not self.scene:
            return
        
        self.title_edit.setText(self.scene.title or "")
        self.beat_edit.setText(self.scene.beat or "")
        self.summary_edit.setPlainText(self.scene.summary or "")
        self.exclude_ai_checkbox.setChecked(self.scene.exclude_from_ai)
    
    def _save_scene(self) -> None:
        """Save the scene to database."""
        # Validate required fields
        title = self.title_edit.text().strip()
        if not title:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Missing Title",
                "Please enter a title for the scene."
            )
            self.title_edit.setFocus()
            return
        
        # Collect data
        data = {
            "title": title,
            "beat": self.beat_edit.text().strip() or None,
            "summary": self.summary_edit.toPlainText().strip() or None,
            "exclude_from_ai": self.exclude_ai_checkbox.isChecked(),
        }
        
        try:
            if self.is_editing:
                # Update existing scene
                for key, value in data.items():
                    setattr(self.scene, key, value)
                self.app_context.commit()
            else:
                # Create new scene
                # Get max position for ordering
                from nico.domain.models import Chapter
                chapter = self.app_context._session.query(Chapter).get(self.chapter_id)
                if chapter:
                    max_position = len(chapter.scenes)
                    
                    scene = Scene(
                        chapter_id=self.chapter_id,
                        position=max_position,
                        content="",  # Empty content initially
                        word_count=0,
                        **data
                    )
                    self.app_context._session.add(scene)
                    self.app_context.commit()
                else:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Could not find the parent chapter."
                    )
                    return
            
            self.accept()
            
        except Exception as e:
            self.app_context.rollback()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while saving the scene:\n{str(e)}"
            )
