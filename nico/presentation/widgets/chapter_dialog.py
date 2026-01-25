"""Chapter creation and editing dialog."""
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
    QSpinBox,
)

from nico.domain.models import Chapter
from nico.application.context import get_app_context


class ChapterDialog(QDialog):
    """Dialog for creating or editing a chapter."""
    
    def __init__(self, story_id: int, chapter: Optional[Chapter] = None, parent=None):
        super().__init__(parent)
        self.story_id = story_id
        self.chapter = chapter
        self.is_editing = chapter is not None
        self.app_context = get_app_context()
        
        self.setWindowTitle("Edit Chapter" if self.is_editing else "New Chapter")
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        
        self._setup_ui()
        if self.is_editing:
            self._load_chapter_data()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Form layout for fields
        form = QFormLayout()
        
        # Title (required)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter chapter title...")
        form.addRow("Title:*", self.title_edit)
        
        # Number (optional)
        self.number_spin = QSpinBox()
        self.number_spin.setRange(0, 1000)
        self.number_spin.setValue(0)
        self.number_spin.setSpecialValueText("Auto")
        self.number_spin.setToolTip("Chapter number (leave as Auto to auto-assign)")
        form.addRow("Number:", self.number_spin)
        
        # Description (optional)
        self.description_edit = QTextEdit()
        self.description_edit.setAcceptRichText(False)
        self.description_edit.setPlaceholderText("Chapter synopsis, notes, or outline...")
        self.description_edit.setMaximumHeight(150)
        form.addRow("Description:", self.description_edit)
        
        # Exclude from AI
        self.exclude_ai_checkbox = QCheckBox("Exclude this chapter from AI context")
        self.exclude_ai_checkbox.setToolTip(
            "When checked, this chapter's content won't be sent to AI models"
        )
        form.addRow("AI Privacy:", self.exclude_ai_checkbox)
        
        layout.addLayout(form)
        
        # Required field note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
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
        save_btn.clicked.connect(self._save_chapter)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _load_chapter_data(self) -> None:
        """Load existing chapter data into the form."""
        if not self.chapter:
            return
        
        self.title_edit.setText(self.chapter.title or "")
        self.description_edit.setPlainText(self.chapter.description or "")
        
        if self.chapter.number:
            self.number_spin.setValue(self.chapter.number)
        else:
            self.number_spin.setValue(0)
        
        self.exclude_ai_checkbox.setChecked(self.chapter.exclude_from_ai)
    
    def _save_chapter(self) -> None:
        """Save the chapter to database."""
        # Validate required fields
        title = self.title_edit.text().strip()
        if not title:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Missing Title",
                "Please enter a title for the chapter."
            )
            self.title_edit.setFocus()
            return
        
        # Collect data
        data = {
            "title": title,
            "description": self.description_edit.toPlainText().strip() or None,
            "number": self.number_spin.value() if self.number_spin.value() > 0 else None,
            "exclude_from_ai": self.exclude_ai_checkbox.isChecked(),
        }
        
        try:
            if self.is_editing:
                # Update existing chapter
                for key, value in data.items():
                    setattr(self.chapter, key, value)
                self.app_context.commit()
            else:
                # Create new chapter
                # Get max position for ordering
                from nico.domain.models import Story
                story = self.app_context._session.query(Story).get(self.story_id)
                if story:
                    max_position = len(story.chapters)
                    
                    chapter = Chapter(
                        story_id=self.story_id,
                        position=max_position,
                        **data
                    )
                    self.app_context._session.add(chapter)
                    self.app_context.commit()
                else:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Could not find the parent story."
                    )
                    return
            
            self.accept()
            
        except Exception as e:
            self.app_context.rollback()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while saving the chapter:\n{str(e)}"
            )
