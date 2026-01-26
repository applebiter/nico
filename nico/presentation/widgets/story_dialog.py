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

from nico.domain.models import Story, WorldBuildingTable, StoryTemplate
from nico.application.context import get_app_context
from nico.presentation.widgets.searchable_combo import SearchableComboBox


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
        
        # Store templates for later use
        self._templates = []
        
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
        
        # Genre (with random button)
        genre_layout = QHBoxLayout()
        self.genre_edit = SearchableComboBox()
        self.genre_edit.setEditable(True)
        genres = self._get_genres()
        if genres:
            self.genre_edit.setItems(genres)
        self.genre_edit.lineEdit().setPlaceholderText("Select or type genre (141 options)")
        
        random_genre_btn = QPushButton("🎲")
        random_genre_btn.setMaximumWidth(40)
        random_genre_btn.setToolTip("Random genre")
        random_genre_btn.clicked.connect(self._randomize_genre)
        
        genre_layout.addWidget(self.genre_edit)
        genre_layout.addWidget(random_genre_btn)
        form.addRow("Genre:", genre_layout)
        
        # Template selection (optional)
        template_layout = QHBoxLayout()
        self.template_combo = SearchableComboBox()
        self.template_combo.setEditable(False)
        templates = self._get_templates()
        template_items = ["(No template - blank story)"] + [f"{t.name} ({t.get_chapter_count()} chapters, {t.genre})" for t in templates]
        self.template_combo.setItems(template_items, sort=False)
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        
        template_layout.addWidget(self.template_combo)
        form.addRow("Story Template:", template_layout)
        
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
    
    def _get_genres(self) -> list[str]:
        """Get list of genres from database."""
        table = self.app_context._session.query(WorldBuildingTable).filter_by(
            table_name="what_kind_of_story__).genre"
        ).first()
        return table.items if table else []
    
    def _get_templates(self) -> list[StoryTemplate]:
        """Get list of story templates from database."""
        self._templates = self.app_context._session.query(StoryTemplate).order_by(StoryTemplate.name).all()
        return self._templates
    
    def _randomize_genre(self) -> None:
        """Pick a random genre."""
        if self.genre_edit.count() > 0:
            import random
            index = random.randint(0, self.genre_edit.count() - 1)
            text = self.genre_edit.itemText(index)
            self.genre_edit.setEditText(text)
    
    def _on_template_changed(self, index: int) -> None:
        """Handle template selection change."""
        if index == 0:
            # No template selected
            return
        
        # Get the selected template (index-1 because of "No template" option)
        template_index = index - 1
        if 0 <= template_index < len(self._templates):
            template = self._templates[template_index]
            
            # Auto-fill genre from template
            if template.genre:
                self.genre_edit.setText(template.genre)
            
            # Update description with template info
            current_desc = self.description_edit.toPlainText().strip()
            template_info = f"\\n\\n[Template: {template.name} - {template.get_chapter_count()} chapters, {len(template.act_structure)} acts]"
            
            if not current_desc:
                self.description_edit.setPlainText(template.description or template_info.strip())
            elif "[Template:" not in current_desc:
                self.description_edit.setPlainText(current_desc + template_info)
    
    def _add_genre_to_table(self, genre: str) -> None:
        """Add a new genre to the genre table if it doesn't exist."""
        genre_table = self.app_context._session.query(WorldBuildingTable).filter_by(
            table_name="what_kind_of_story__).genre"
        ).first()
        
        if genre_table:
            # Check if genre already exists (case-insensitive)
            existing_genres_lower = [g.lower() for g in genre_table.items]
            if genre.lower() not in existing_genres_lower:
                # Add new genre and sort alphabetically
                genre_table.items = sorted(genre_table.items + [genre], key=str.lower)
                # Refresh the combo box
                self.genre_edit.clear()
                self.genre_edit.setItems(genre_table.items)
                self.genre_edit.setText(genre)
    
    def _load_story_data(self) -> None:
        """Load existing story data into the form."""
        if not self.story:
            return
        
        self.title_edit.setText(self.story.title or "")
        self.subtitle_edit.setText(self.story.subtitle or "")
        
        # Load genre from meta field
        if self.story.meta and 'genre' in self.story.meta:
            self.genre_edit.setText(self.story.meta['genre'])
        
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
        
        # Add genre to meta field and update genre table if new
        genre = self.genre_edit.currentText().strip()
        if genre:
            # Add to story meta
            if self.is_editing and self.story.meta:
                meta = self.story.meta.copy()
            else:
                meta = {}
            meta['genre'] = genre
            data['meta'] = meta
            
            # Check if genre exists in table, add if new
            self._add_genre_to_table(genre)
        
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
