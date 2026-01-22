"""Dialog for selecting and customizing story templates."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QTextEdit,
    QSpinBox, QCheckBox, QScrollArea, QWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from nico.templates import TemplateLibrary, StoryTemplate
from nico.application.generators import TemplateCustomizer


class TemplateSelectionDialog(QDialog):
    """Dialog for selecting a story template and customizing it."""
    
    template_accepted = Signal(object, object)  # (template, customization_dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Story from Template")
        self.resize(800, 600)
        
        self.templates = TemplateLibrary.get_all_templates()
        self.current_template = None
        self.customization_widgets = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Template selection
        template_group = QGroupBox("Select Template")
        template_layout = QVBoxLayout()
        
        self.template_combo = QComboBox()
        for template in self.templates:
            self.template_combo.addItem(
                f"{template.name} ({template.genre.value})",
                template
            )
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        template_layout.addWidget(self.template_combo)
        
        # Template description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        template_layout.addWidget(self.description_label)
        
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
        # Customization area (scroll area for long forms)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.customization_widget = QWidget()
        self.customization_layout = QVBoxLayout(self.customization_widget)
        scroll.setWidget(self.customization_widget)
        
        layout.addWidget(scroll, 1)  # Give it stretch factor
        
        # Story title override
        title_group = QGroupBox("Story Settings")
        title_layout = QFormLayout()
        
        self.story_title_edit = QLineEdit()
        self.story_title_edit.setPlaceholderText("Leave empty to use template name")
        title_layout.addRow("Story Title:", self.story_title_edit)
        
        title_group.setLayout(title_layout)
        layout.addWidget(title_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        preview_btn = QPushButton("Preview Outline")
        preview_btn.clicked.connect(self._show_preview)
        button_layout.addWidget(preview_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        generate_btn = QPushButton("Generate Story")
        generate_btn.setDefault(True)
        generate_btn.clicked.connect(self._generate)
        button_layout.addWidget(generate_btn)
        
        layout.addLayout(button_layout)
        
        # Load first template
        self._on_template_changed(0)
    
    def _on_template_changed(self, index: int):
        """Update customization form when template changes."""
        template = self.template_combo.itemData(index)
        if not template:
            return
        
        self.current_template = template
        
        # Update description
        desc_parts = [template.description]
        if template.target_word_count:
            desc_parts.append(f"Target length: ~{template.target_word_count:,} words")
        desc_parts.append(f"Chapters: {len(template.chapters)}")
        self.description_label.setText(" • ".join(desc_parts))
        
        # Clear previous customization widgets
        while self.customization_layout.count():
            item = self.customization_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.customization_widgets = {}
        
        # Create genre-specific customization form
        if template.genre.name == "ROMANCE":
            self._create_romance_customization()
        elif template.genre.name == "HERO_JOURNEY":
            self._create_hero_journey_customization()
        else:
            self._create_generic_customization()
    
    def _create_romance_customization(self):
        """Create customization form for romance template."""
        group = QGroupBox("Character Names")
        form = QFormLayout()
        
        protagonist_edit = QLineEdit()
        protagonist_edit.setPlaceholderText("e.g., Emma")
        form.addRow("Protagonist:", protagonist_edit)
        self.customization_widgets["protagonist"] = protagonist_edit
        
        love_interest_edit = QLineEdit()
        love_interest_edit.setPlaceholderText("e.g., Liam")
        form.addRow("Love Interest:", love_interest_edit)
        self.customization_widgets["love_interest"] = love_interest_edit
        
        group.setLayout(form)
        self.customization_layout.addWidget(group)
        
        # Setting group
        setting_group = QGroupBox("Setting & Details")
        setting_form = QFormLayout()
        
        setting_combo = QComboBox()
        setting_combo.addItems(["Contemporary", "Historical", "Fantasy", "Sci-Fi", "Custom"])
        setting_form.addRow("Setting Type:", setting_combo)
        self.customization_widgets["setting"] = setting_combo
        
        protagonist_job = QLineEdit()
        protagonist_job.setPlaceholderText("e.g., Artist, CEO, Teacher")
        setting_form.addRow("Protagonist's Job:", protagonist_job)
        self.customization_widgets["protagonist_job"] = protagonist_job
        
        love_interest_job = QLineEdit()
        love_interest_job.setPlaceholderText("e.g., Doctor, Writer, Chef")
        setting_form.addRow("Love Interest's Job:", love_interest_job)
        self.customization_widgets["love_interest_job"] = love_interest_job
        
        setting_group.setLayout(setting_form)
        self.customization_layout.addWidget(setting_group)
        
        # Chapter options
        self._add_chapter_options()
    
    def _create_hero_journey_customization(self):
        """Create customization form for hero's journey template."""
        group = QGroupBox("Character Names")
        form = QFormLayout()
        
        hero_edit = QLineEdit()
        hero_edit.setPlaceholderText("e.g., Aria")
        form.addRow("Hero:", hero_edit)
        self.customization_widgets["hero"] = hero_edit
        
        mentor_edit = QLineEdit()
        mentor_edit.setPlaceholderText("e.g., Master Toren")
        form.addRow("Mentor:", mentor_edit)
        self.customization_widgets["mentor"] = mentor_edit
        
        villain_edit = QLineEdit()
        villain_edit.setPlaceholderText("e.g., Lord Darkness")
        form.addRow("Villain/Shadow:", villain_edit)
        self.customization_widgets["villain"] = villain_edit
        
        group.setLayout(form)
        self.customization_layout.addWidget(group)
        
        # Quest details
        quest_group = QGroupBox("Quest Details")
        quest_form = QFormLayout()
        
        quest_edit = QLineEdit()
        quest_edit.setPlaceholderText("e.g., the Crystal of Power")
        quest_form.addRow("Quest Object:", quest_edit)
        self.customization_widgets["quest_object"] = quest_edit
        
        quest_group.setLayout(quest_form)
        self.customization_layout.addWidget(quest_group)
        
        # Chapter options
        self._add_chapter_options()
    
    def _create_generic_customization(self):
        """Create generic customization form."""
        group = QGroupBox("Character Names")
        form = QFormLayout()
        
        # Add fields for character archetypes
        if self.current_template and self.current_template.character_archetypes:
            for archetype in self.current_template.character_archetypes[:5]:  # Limit to first 5
                name = archetype.get("name", "Character")
                edit = QLineEdit()
                edit.setPlaceholderText(f"Name for {name}")
                form.addRow(f"{name}:", edit)
                self.customization_widgets[f"char_{name}"] = edit
        
        group.setLayout(form)
        self.customization_layout.addWidget(group)
        
        # Chapter options
        self._add_chapter_options()
    
    def _add_chapter_options(self):
        """Add chapter customization options."""
        if not self.current_template:
            return
        
        group = QGroupBox("Chapter Options (Optional)")
        layout = QVBoxLayout()
        
        info_label = QLabel(
            f"Template has {len(self.current_template.chapters)} chapters. "
            "You can skip specific chapters if desired."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888;")
        layout.addWidget(info_label)
        
        # Skip chapters checkboxes
        skip_layout = QVBoxLayout()
        self.customization_widgets["skip_chapters"] = []
        
        for chapter in self.current_template.chapters[:5]:  # Show first 5
            checkbox = QCheckBox(f"Skip Chapter {chapter.number}: {chapter.title}")
            skip_layout.addWidget(checkbox)
            self.customization_widgets["skip_chapters"].append(checkbox)
        
        if len(self.current_template.chapters) > 5:
            more_label = QLabel(f"... and {len(self.current_template.chapters) - 5} more chapters")
            more_label.setStyleSheet("color: #888; font-style: italic;")
            skip_layout.addWidget(more_label)
        
        layout.addLayout(skip_layout)
        
        group.setLayout(layout)
        self.customization_layout.addWidget(group)
        
        # Add stretch at end
        self.customization_layout.addStretch()
    
    def _get_customization_dict(self) -> dict:
        """Build customization dictionary from form values."""
        if not self.current_template:
            return {}
        
        customization = {}
        
        # Genre-specific customization
        if self.current_template.genre.name == "ROMANCE":
            protagonist = self.customization_widgets.get("protagonist")
            love_interest = self.customization_widgets.get("love_interest")
            setting = self.customization_widgets.get("setting")
            protagonist_job = self.customization_widgets.get("protagonist_job")
            love_interest_job = self.customization_widgets.get("love_interest_job")
            
            if protagonist and protagonist.text():
                if love_interest and love_interest.text():
                    customization = TemplateCustomizer.customize_romance_template(
                        protagonist_name=protagonist.text(),
                        love_interest_name=love_interest.text(),
                        setting=setting.currentText() if setting else "Contemporary",
                        occupation_protagonist=protagonist_job.text() if protagonist_job and protagonist_job.text() else None,
                        occupation_love_interest=love_interest_job.text() if love_interest_job and love_interest_job.text() else None,
                    )
        
        elif self.current_template.genre.name == "HERO_JOURNEY":
            hero = self.customization_widgets.get("hero")
            mentor = self.customization_widgets.get("mentor")
            villain = self.customization_widgets.get("villain")
            quest = self.customization_widgets.get("quest_object")
            
            if hero and hero.text():
                customization = TemplateCustomizer.customize_heros_journey(
                    hero_name=hero.text(),
                    mentor_name=mentor.text() if mentor and mentor.text() else None,
                    villain_name=villain.text() if villain and villain.text() else None,
                    quest_object=quest.text() if quest and quest.text() else "the ancient artifact",
                )
        
        else:
            # Generic character mapping
            character_names = {}
            for key, widget in self.customization_widgets.items():
                if key.startswith("char_") and isinstance(widget, QLineEdit) and widget.text():
                    archetype_name = key.replace("char_", "")
                    character_names[archetype_name] = widget.text()
            if character_names:
                customization["character_names"] = character_names
        
        # Skip chapters
        skip_chapters = []
        if "skip_chapters" in self.customization_widgets:
            for i, checkbox in enumerate(self.customization_widgets["skip_chapters"]):
                if checkbox.isChecked():
                    skip_chapters.append(self.current_template.chapters[i].number)
        if skip_chapters:
            customization["skip_chapters"] = skip_chapters
        
        return customization
    
    def _show_preview(self):
        """Show preview of story structure."""
        if not self.current_template:
            return
        
        from nico.application.generators import StoryGenerator
        
        customization = self._get_customization_dict()
        character_names = customization.get("character_names", {})
        
        # Generate outline (no database interaction)
        generator = StoryGenerator(None)
        outline = generator.generate_outline_only(
            self.current_template,
            character_names=character_names
        )
        
        # Display in dialog
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("Story Structure Preview")
        preview_dialog.resize(600, 500)
        
        layout = QVBoxLayout(preview_dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Format outline as text
        content = []
        content.append(f"# {outline['title']}\n")
        content.append(f"{outline['description']}\n")
        content.append(f"Genre: {outline['genre']}\n")
        if outline.get('target_word_count'):
            content.append(f"Target: ~{outline['target_word_count']:,} words\n")
        content.append("\n---\n\n")
        
        for chapter in outline['chapters']:
            content.append(f"## Chapter {chapter['number']}: {chapter['title']}\n")
            if chapter.get('description'):
                content.append(f"_{chapter['description']}_\n")
            content.append("\n")
            
            for scene in chapter['scenes']:
                content.append(f"  **{scene['title']}**")
                if scene.get('beat'):
                    content.append(f" [{scene['beat']}]")
                content.append("\n")
                
                if scene.get('description'):
                    content.append(f"  {scene['description']}\n")
                if scene.get('characters'):
                    content.append(f"  Characters: {', '.join(scene['characters'])}\n")
                content.append("\n")
        
        text_edit.setPlainText("".join(content))
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(preview_dialog.accept)
        layout.addWidget(close_btn)
        
        preview_dialog.exec()
    
    def _generate(self):
        """Accept dialog and emit template with customization."""
        if not self.current_template:
            QMessageBox.warning(self, "No Template", "Please select a template.")
            return
        
        customization = self._get_customization_dict()
        
        # Get story title override
        story_title = self.story_title_edit.text().strip() or None
        if story_title:
            customization["story_title"] = story_title
        
        self.template_accepted.emit(self.current_template, customization)
        self.accept()
