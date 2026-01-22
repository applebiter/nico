"""Story creation and editing dialog."""
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

from nico.domain.models import Story
from nico.application.context import get_app_context


class StoryDialog(QDialog):
    """Dialog for creating or editing a story."""
    
    def __init__(self, project_id: int, story: Optional[Story] = None, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.story = story
        self.is_editing = story is not None
        self.app_context = get_app_context()
        
        self.setWindowTitle("Edit Story" if self.is_editing else "New Story")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self._setup_ui()
        if self.is_editing:
            self._load_story_data()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Form layout for fields
        form = QFormLayout()
        
        # Title (required)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter story title...")
        form.addRow("Title:*", self.title_edit)
        
        # Subtitle (optional)
        self.subtitle_edit = QLineEdit()
        self.subtitle_edit.setPlaceholderText("Optional subtitle")
        form.addRow("Subtitle:", self.subtitle_edit)
        
        # Description (optional)
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Story synopsis or description...")
        self.description_edit.setMaximumHeight(150)
        form.addRow("Description:", self.description_edit)
        
        # Fiction/Non-fiction toggle
        self.is_fiction_checkbox = QCheckBox("Fiction (uncheck for non-fiction)")
        self.is_fiction_checkbox.setChecked(True)
        form.addRow("Type:", self.is_fiction_checkbox)
        
        # Word count target
        self.target_words = QSpinBox()
        self.target_words.setRange(0, 1000000)
        self.target_words.setSingleStep(1000)
        self.target_words.setValue(80000)
        self.target_words.setSuffix(" words")
        self.target_words.setSpecialValueText("No target")
        form.addRow("Target Word Count:", self.target_words)
        
        # Exclude from AI
        self.exclude_ai_checkbox = QCheckBox("Exclude this story from AI context")
        self.exclude_ai_checkbox.setToolTip(
            "When checked, this story's content won't be sent to AI models"
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
        save_btn.clicked.connect(self._save_story)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _load_story_data(self) -> None:
        """Load existing story data into the form."""
        if not self.story:
            return
        
        self.title_edit.setText(self.story.title or "")
        self.subtitle_edit.setText(self.story.subtitle or "")
        self.description_edit.setPlainText(self.story.description or "")
        self.is_fiction_checkbox.setChecked(self.story.is_fiction)
        
        if self.story.word_count_target:
            self.target_words.setValue(self.story.word_count_target)
        else:
            self.target_words.setValue(0)
        
        self.exclude_ai_checkbox.setChecked(self.story.exclude_from_ai)
    
    def _save_story(self) -> None:
        """Save the story to database."""
        # Validate required fields
        title = self.title_edit.text().strip()
        if not title:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Missing Title",
                "Please enter a title for the story."
            )
            self.title_edit.setFocus()
            return
        
        # Collect data
        data = {
            "title": title,
            "subtitle": self.subtitle_edit.text().strip() or None,
            "description": self.description_edit.toPlainText().strip() or None,
            "is_fiction": self.is_fiction_checkbox.isChecked(),
            "word_count_target": self.target_words.value() if self.target_words.value() > 0 else None,
            "exclude_from_ai": self.exclude_ai_checkbox.isChecked(),
        }
        
        try:
            if self.is_editing:
                # Update existing story
                for key, value in data.items():
                    if hasattr(self.story, key):
                        setattr(self.story, key, value)
                # Use session to merge changes
                if hasattr(self.app_context, '_session') and self.app_context._session:
                    self.app_context._session.merge(self.story)
            else:
                # Create new story
                from nico.domain.models import Story
                
                # Get the next position
                project = self.app_context.project_service.get_project(self.project_id)
                next_position = len(project.stories) if project else 0
                
                story = Story(
                    project_id=self.project_id,
                    position=next_position,
                    **data
                )
                
                if hasattr(self.app_context, '_session') and self.app_context._session:
                    self.app_context._session.add(story)
            
            self.app_context.commit()
            self.accept()
            
        except Exception as e:
            self.app_context.rollback()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error",
                f"Error saving story: {str(e)}"
            )
