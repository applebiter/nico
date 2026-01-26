"""Character profile viewer widget."""
from typing import Optional
import asyncio
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QGroupBox,
    QTextEdit,
    QFrame,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QProgressBar,
    QSizePolicy,
)
from PySide6.QtGui import QPixmap

from nico.domain.models import Character
from nico.application.context import get_app_context
from nico.presentation.widgets.character_dialog import CharacterDialog
from nico.infrastructure.comfyui_service import get_comfyui_service


class ImageGenerationWorker(QObject):
    """Worker for generating images in a background thread."""
    finished = Signal(object)  # image_path or None
    error = Signal(str)  # error message
    
    def __init__(self, prompt: str, project_path: Path, width: int = 1024, height: int = 1024, seed: int = None):
        super().__init__()
        self.prompt = prompt
        self.project_path = project_path
        self.width = width
        self.height = height
        self.seed = seed
    
    def run(self):
        """Generate image using ComfyUI."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Get ComfyUI service and generate image
            comfyui = get_comfyui_service(project_path=self.project_path)
            image_path = loop.run_until_complete(
                comfyui.generate_image(self.prompt, width=self.width, height=self.height, seed=self.seed)
            )
            
            loop.close()
            
            self.finished.emit(image_path)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class CharacterProfileWidget(QWidget):
    """Widget for viewing and editing character profiles."""
    
    # Signal emitted when character is updated
    character_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_character: Optional[Character] = None
        self.app_context = get_app_context()
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(15)
        
        # Header section
        self._create_header_section()
        
        # Image section
        self._create_image_section()
        
        # Basic info section
        self._create_basic_info_section()
        
        # Identity section
        self._create_identity_section()
        
        # Life details section
        self._create_life_section()
        
        # Psychology section
        self._create_psychology_section()
        
        content.setLayout(self.content_layout)
        scroll.setWidget(content)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
        
        # Initially hide all sections
        self._set_visibility(False)
    
    def _create_header_section(self) -> None:
        """Create the header with character name and actions."""
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Character name
        self.name_label = QLabel()
        self.name_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(self.name_label)
        
        header_layout.addStretch()
        
        # Add New button
        self.add_new_btn = QPushButton("➕ Add New")
        self.add_new_btn.clicked.connect(self._on_add_new_character)
        header_layout.addWidget(self.add_new_btn)
        
        # Edit button
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self._on_edit_character)
        header_layout.addWidget(self.edit_btn)
        
        # Delete button
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self._on_delete_character)
        header_layout.addWidget(self.delete_btn)
        
        header_widget.setLayout(header_layout)
        self.content_layout.addWidget(header_widget)
        self.header_widget = header_widget
    
    def _create_image_section(self) -> None:
        """Create the character image section with generation button."""
        self.image_group = QGroupBox("Character Portrait")
        image_layout = QVBoxLayout()
        
        # Image display
        image_container = QWidget()
        image_container_layout = QHBoxLayout()
        image_container_layout.addStretch()
        
        self.image_label = QLabel()
        self.image_label.setMinimumSize(256, 256)
        self.image_label.setScaledContents(False)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #555;
                border-radius: 8px;
                background-color: #2a2a2a;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.image_label.mousePressEvent = self._on_portrait_clicked
        image_container_layout.addWidget(self.image_label)
        image_container_layout.addStretch()
        image_container.setLayout(image_container_layout)
        image_container.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        image_layout.addWidget(image_container)
        
        # Image generation controls
        gen_layout = QHBoxLayout()
        
        # Upload button (first)
        self.upload_image_btn = QPushButton("📁 Upload")
        self.upload_image_btn.clicked.connect(self._on_upload_image)
        gen_layout.addWidget(self.upload_image_btn)
        
        # Clear button
        self.clear_image_btn = QPushButton("🗑️ Clear")
        self.clear_image_btn.clicked.connect(self._on_clear_image)
        self.clear_image_btn.setToolTip("Remove current portrait")
        gen_layout.addWidget(self.clear_image_btn)
        
        # Generate button
        self.generate_image_btn = QPushButton("🎨 Generate")
        self.generate_image_btn.clicked.connect(self._on_generate_image)
        self.generate_image_btn.setToolTip("Generate character portrait using z-image-turbo")
        gen_layout.addWidget(self.generate_image_btn)
        
        # Dimension preset dropdown
        self.dimension_preset = QComboBox()
        self.dimension_preset.addItems([
            "Square 1024×1024",
            "Portrait 832×1216",
            "Portrait 896×1152",
            "Landscape 1216×832",
            "Landscape 1152×896",
            "Wide 1344×768",
            "Wide 1536×640",
            "Tall 768×1344",
            "Tall 640×1536",
            "Custom"
        ])
        self.dimension_preset.setCurrentIndex(0)
        self.dimension_preset.currentTextChanged.connect(self._on_dimension_preset_changed)
        gen_layout.addWidget(QLabel("Size:"))
        gen_layout.addWidget(self.dimension_preset)
        
        # Custom width/height spinboxes
        self.width_spin = QSpinBox()
        self.width_spin.setRange(256, 2048)
        self.width_spin.setSingleStep(64)
        self.width_spin.setValue(1024)
        self.width_spin.setPrefix("W: ")
        self.width_spin.setEnabled(False)
        gen_layout.addWidget(self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(256, 2048)
        self.height_spin.setSingleStep(64)
        self.height_spin.setValue(1024)
        self.height_spin.setPrefix("H: ")
        self.height_spin.setEnabled(False)
        gen_layout.addWidget(self.height_spin)
        
        # Optional seed
        gen_layout.addWidget(QLabel("Seed:"))
        self.seed_input = QLineEdit()
        self.seed_input.setPlaceholderText("Optional")
        self.seed_input.setMaximumWidth(100)
        self.seed_input.setToolTip("Leave empty for random seed")
        gen_layout.addWidget(self.seed_input)
        
        gen_layout.addStretch()
        image_layout.addLayout(gen_layout)
        
        # Progress bar for image generation
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Generating portrait...")
        self.progress_bar.hide()  # Hidden by default
        image_layout.addWidget(self.progress_bar)
        
        self.image_group.setLayout(image_layout)
        self.content_layout.addWidget(self.image_group)
    
    def _create_basic_info_section(self) -> None:
        """Create the basic info section."""
        self.basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Mr., Dr., Sir, etc.")
        basic_layout.addRow("Title:", self.title_edit)
        
        self.full_name_value = QLabel()
        self.full_name_value.setStyleSheet("color: #888; font-style: italic;")
        basic_layout.addRow("Full Name:", self.full_name_value)
        
        self.nickname_edit = QLineEdit()
        self.nickname_edit.setPlaceholderText("Preferred name or nickname")
        basic_layout.addRow("Nickname:", self.nickname_edit)
        
        self.physical_value = QTextEdit()
        self.physical_value.setMinimumHeight(160)  # Approximately 8 lines
        self.physical_value.setPlaceholderText("Describe the character's physical appearance...")
        self.physical_value.textChanged.connect(self._on_physical_description_changed)
        basic_layout.addRow("Physical Description:", self.physical_value)
        
        self.basic_group.setLayout(basic_layout)
        self.content_layout.addWidget(self.basic_group)
    
    def _create_identity_section(self) -> None:
        """Create the identity section."""
        self.identity_group = QGroupBox("Identity")
        identity_layout = QFormLayout()
        
        self.gender_edit = QLineEdit()
        self.gender_edit.setPlaceholderText("Gender identity")
        identity_layout.addRow("Gender:", self.gender_edit)
        
        self.ethnicity_edit = QLineEdit()
        self.ethnicity_edit.setPlaceholderText("Ethnic background")
        identity_layout.addRow("Ethnicity:", self.ethnicity_edit)
        
        self.nationality_edit = QLineEdit()
        self.nationality_edit.setPlaceholderText("National origin")
        identity_layout.addRow("Nationality:", self.nationality_edit)
        
        self.religion_edit = QLineEdit()
        self.religion_edit.setPlaceholderText("Religious affiliation")
        identity_layout.addRow("Religion:", self.religion_edit)
        
        self.identity_group.setLayout(identity_layout)
        self.content_layout.addWidget(self.identity_group)
    
    def _create_life_section(self) -> None:
        """Create the life details section."""
        self.life_group = QGroupBox("Life Details")
        life_layout = QFormLayout()
        
        self.occupation_edit = QLineEdit()
        self.occupation_edit.setPlaceholderText("Current occupation")
        life_layout.addRow("Occupation:", self.occupation_edit)
        
        self.education_edit = QLineEdit()
        self.education_edit.setPlaceholderText("Educational background")
        life_layout.addRow("Education:", self.education_edit)
        
        self.marital_edit = QLineEdit()
        self.marital_edit.setPlaceholderText("Marital status")
        life_layout.addRow("Marital Status:", self.marital_edit)
        
        self.dob_edit = QLineEdit()
        self.dob_edit.setPlaceholderText("Date of birth")
        life_layout.addRow("Date of Birth:", self.dob_edit)
        
        self.dod_edit = QLineEdit()
        self.dod_edit.setPlaceholderText("Date of death (if applicable)")
        life_layout.addRow("Date of Death:", self.dod_edit)
        
        self.life_group.setLayout(life_layout)
        self.content_layout.addWidget(self.life_group)
    
    def _create_psychology_section(self) -> None:
        """Create the psychology section."""
        self.psychology_group = QGroupBox("Psychology")
        psych_layout = QFormLayout()
        
        self.myers_briggs_edit = QLineEdit()
        self.myers_briggs_edit.setPlaceholderText("e.g., INTJ, ENFP")
        psych_layout.addRow("Myers-Briggs:", self.myers_briggs_edit)
        
        self.enneagram_edit = QLineEdit()
        self.enneagram_edit.setPlaceholderText("e.g., Type 4w5")
        psych_layout.addRow("Enneagram:", self.enneagram_edit)
        
        self.wounds_value = QTextEdit()
        self.wounds_value.setMaximumHeight(80)
        self.wounds_value.setPlaceholderText("Emotional wounds, traumas, fears...")
        psych_layout.addRow("Wounds:", self.wounds_value)
        
        self.psychology_group.setLayout(psych_layout)
        self.content_layout.addWidget(self.psychology_group)
        
        # Add save/cancel buttons
        self._create_action_buttons()
    
    def _create_action_buttons(self) -> None:
        """Create save/revert buttons at the bottom."""
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.clicked.connect(self._on_save_changes)
        self.save_btn.setEnabled(False)  # Disabled until changes are made
        button_layout.addWidget(self.save_btn)
        
        self.revert_btn = QPushButton("↺ Revert")
        self.revert_btn.clicked.connect(self._on_revert_changes)
        self.revert_btn.setEnabled(False)  # Disabled until changes are made
        button_layout.addWidget(self.revert_btn)
        
        button_widget.setLayout(button_layout)
        self.content_layout.addWidget(button_widget)
        
        # Track changes for all editable fields
        self.title_edit.textChanged.connect(self._on_field_changed)
        self.nickname_edit.textChanged.connect(self._on_field_changed)
        self.gender_edit.textChanged.connect(self._on_field_changed)
        self.ethnicity_edit.textChanged.connect(self._on_field_changed)
        self.nationality_edit.textChanged.connect(self._on_field_changed)
        self.religion_edit.textChanged.connect(self._on_field_changed)
        self.occupation_edit.textChanged.connect(self._on_field_changed)
        self.education_edit.textChanged.connect(self._on_field_changed)
        self.marital_edit.textChanged.connect(self._on_field_changed)
        self.dob_edit.textChanged.connect(self._on_field_changed)
        self.dod_edit.textChanged.connect(self._on_field_changed)
        self.myers_briggs_edit.textChanged.connect(self._on_field_changed)
        self.enneagram_edit.textChanged.connect(self._on_field_changed)
        self.wounds_value.textChanged.connect(self._on_field_changed)
    
    def _on_field_changed(self) -> None:
        """Enable save/revert buttons when fields change."""
        self.save_btn.setEnabled(True)
        self.revert_btn.setEnabled(True)
    
    def _on_save_changes(self) -> None:
        """Save all field changes to database."""
        if not self.current_character:
            return
        
        try:
            # Collect all field values
            updates = {
                'title': self.title_edit.text().strip() or None,
                'nickname': self.nickname_edit.text().strip() or None,
                'physical_description': self.physical_value.toPlainText().strip() or None,
                'gender': self.gender_edit.text().strip() or None,
                'ethnicity': self.ethnicity_edit.text().strip() or None,
                'nationality': self.nationality_edit.text().strip() or None,
                'religion': self.religion_edit.text().strip() or None,
                'occupation': self.occupation_edit.text().strip() or None,
                'education': self.education_edit.text().strip() or None,
                'marital_status': self.marital_edit.text().strip() or None,
                'date_of_birth': self.dob_edit.text().strip() or None,
                'date_of_death': self.dod_edit.text().strip() or None,
                'myers_briggs': self.myers_briggs_edit.text().strip() or None,
                'enneagram': self.enneagram_edit.text().strip() or None,
                'wounds': self.wounds_value.toPlainText().strip() or None,
            }
            
            # Update character
            self.app_context.character_service.update_character(
                self.current_character.id,
                **updates
            )
            self.app_context.commit()
            
            # Reload character to update full name display and ensure consistency
            updated_char = self.app_context.character_service.get_character(self.current_character.id)
            if updated_char:
                self.load_character(updated_char)
            
            # Disable save/revert buttons
            self.save_btn.setEnabled(False)
            self.revert_btn.setEnabled(False)
            
            # Notify other widgets
            self.character_updated.emit()
            
        except Exception as e:
            self.app_context.rollback()
            QMessageBox.warning(self, "Save Error", f"Failed to save changes: {e}")
    
    def _on_revert_changes(self) -> None:
        """Revert all field changes to original values."""
        if self.current_character:
            self._populate_fields()
            self.save_btn.setEnabled(False)
            self.revert_btn.setEnabled(False)
    
    def load_character(self, character: 'Character') -> None:
        """Load and display a character."""
        if character:
            self.current_character = character
            self._populate_fields()
            self._set_visibility(True)
    
    def _populate_fields(self) -> None:
        """Populate all fields with character data."""
        if not self.current_character:
            return
        
        char = self.current_character
        
        # Header
        name_parts = []
        if char.title:
            name_parts.append(char.title)
        if char.first_name:
            name_parts.append(char.first_name)
        if char.middle_names:
            name_parts.append(char.middle_names)
        if char.last_name:
            name_parts.append(char.last_name)
        
        display_name = " ".join(name_parts) if name_parts else "Unnamed Character"
        if char.nickname:
            display_name += f' "{char.nickname}"'
        
        self.name_label.setText(f"👤 {display_name}")
        
        # Load character image if it exists
        if char.image_path:
            from pathlib import Path
            image_file = Path(char.image_path)
            if image_file.exists():
                pixmap = QPixmap(str(image_file))
                if not pixmap.isNull():
                    # Calculate dimensions: scale the larger dimension to max, other proportionally
                    img_width = pixmap.width()
                    img_height = pixmap.height()
                    max_size = 512
                    
                    if img_width >= img_height:
                        # Width is larger - scale to max width
                        display_width = max_size
                        display_height = int((img_height / img_width) * max_size)
                    else:
                        # Height is larger - scale to max height
                        display_height = max_size
                        display_width = int((img_width / img_height) * max_size)
                    
                    self.image_label.setMinimumSize(display_width, display_height)
                    self.image_label.setMaximumSize(display_width, display_height)
                    scaled_pixmap = pixmap.scaled(
                        display_width, display_height,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
            else:
                # Clear image if file no longer exists
                self.image_label.setText("No portrait yet\n\nClick 'Generate Portrait'\nto create one")
        else:
            self.image_label.setText("No portrait yet\n\nClick 'Generate Portrait'\nto create one")
        
        # Disconnect all change signals during population (safely ignore if not connected)
        try:
            self.title_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.nickname_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.physical_value.textChanged.disconnect(self._on_physical_description_changed)
        except RuntimeError:
            pass
        try:
            self.physical_value.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.gender_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.ethnicity_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.nationality_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.religion_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.occupation_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.education_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.marital_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.dob_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.dod_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.myers_briggs_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.enneagram_edit.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        try:
            self.wounds_value.textChanged.disconnect(self._on_field_changed)
        except RuntimeError:
            pass
        
        # Basic info
        self.title_edit.setText(char.title or "")
        full_name = " ".join(filter(None, [char.first_name, char.middle_names, char.last_name]))
        self.full_name_value.setText(full_name or "—")
        self.nickname_edit.setText(char.nickname or "")
        self.physical_value.setPlainText(char.physical_description or "")
        
        # Identity
        self.gender_edit.setText(char.gender or "")
        self.ethnicity_edit.setText(char.ethnicity or "")
        self.nationality_edit.setText(char.nationality or "")
        self.religion_edit.setText(char.religion or "")
        
        # Life
        self.occupation_edit.setText(char.occupation or "")
        self.education_edit.setText(char.education or "")
        self.marital_edit.setText(char.marital_status or "")
        self.dob_edit.setText(str(char.date_of_birth) if char.date_of_birth else "")
        self.dod_edit.setText(str(char.date_of_death) if char.date_of_death else "")
        
        # Psychology
        self.myers_briggs_edit.setText(char.myers_briggs or "")
        self.enneagram_edit.setText(char.enneagram or "")
        self.wounds_value.setPlainText(char.wounds or "")
        
        # Reconnect all change signals
        self.title_edit.textChanged.connect(self._on_field_changed)
        self.nickname_edit.textChanged.connect(self._on_field_changed)
        self.physical_value.textChanged.connect(self._on_physical_description_changed)
        self.physical_value.textChanged.connect(self._on_field_changed)
        self.gender_edit.textChanged.connect(self._on_field_changed)
        self.ethnicity_edit.textChanged.connect(self._on_field_changed)
        self.nationality_edit.textChanged.connect(self._on_field_changed)
        self.religion_edit.textChanged.connect(self._on_field_changed)
        self.occupation_edit.textChanged.connect(self._on_field_changed)
        self.education_edit.textChanged.connect(self._on_field_changed)
        self.marital_edit.textChanged.connect(self._on_field_changed)
        self.dob_edit.textChanged.connect(self._on_field_changed)
        self.dod_edit.textChanged.connect(self._on_field_changed)
        self.myers_briggs_edit.textChanged.connect(self._on_field_changed)
        self.enneagram_edit.textChanged.connect(self._on_field_changed)
        self.wounds_value.textChanged.connect(self._on_field_changed)
        
        # Disable save/revert buttons after population
        self.save_btn.setEnabled(False)
        self.revert_btn.setEnabled(False)
    
    def _set_visibility(self, visible: bool) -> None:
        """Show or hide all content sections."""
        self.header_widget.setVisible(visible)
        self.image_group.setVisible(visible)
        self.basic_group.setVisible(visible)
        self.identity_group.setVisible(visible)
        self.life_group.setVisible(visible)
        self.psychology_group.setVisible(visible)
    
    def _on_physical_description_changed(self) -> None:
        """Auto-save physical description changes."""
        if not self.current_character:
            return
        
        # Get the updated text
        new_description = self.physical_value.toPlainText()
        
        # Only save if it actually changed
        if new_description != (self.current_character.physical_description or ""):
            try:
                self.app_context.character_service.update_character(
                    self.current_character.id,
                    physical_description=new_description or None
                )
                self.app_context.commit()
                # Update the local character object
                self.current_character.physical_description = new_description or None
            except Exception as e:
                self.app_context.rollback()
                print(f"Error auto-saving physical description: {e}")
    
    
    def _on_add_new_character(self) -> None:
        """Open the character creation dialog."""
        # Get the project from the current character or app context
        project_id = None
        if self.current_character:
            project_id = self.current_character.project_id
        else:
            # Get first available project
            projects = self.app_context.project_service.list_projects()
            if projects:
                project_id = projects[0].id
        
        if not project_id:
            QMessageBox.warning(
                self,
                "No Project",
                "Please create or open a project first."
            )
            return
        
        dialog = CharacterDialog(project_id, parent=self)
        if dialog.exec():
            # Character was created, emit signal to refresh lists
            self.character_updated.emit()
    
    def _on_edit_character(self) -> None:
        """Open the character edit dialog."""
        if not self.current_character:
            return
        
        dialog = CharacterDialog(
            self.current_character.project_id,
            self.current_character,
            parent=self
        )
        if dialog.exec():
            # Reload the character to show updated data
            updated_char = self.app_context.character_service.get_character(self.current_character.id)
            if updated_char:
                self.load_character(updated_char)
            self.character_updated.emit()
    
    def _on_delete_character(self) -> None:
        """Delete the current character after confirmation."""
        if not self.current_character:
            return
        
        # Get character name for display
        name = self.current_character.nickname or self.current_character.first_name or "this character"
        if self.current_character.last_name:
            name += f" {self.current_character.last_name}"
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Character",
            f"Are you sure you want to delete {name}?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete the character
                character_id = self.current_character.id
                success = self.app_context.character_service.delete_character(character_id)
                
                if success:
                    self.app_context.commit()
                    # Clear the display
                    self.current_character = None
                    self._set_visibility(False)
                    # Emit signal to refresh lists
                    self.character_updated.emit()
                    QMessageBox.information(
                        self,
                        "Character Deleted",
                        f"{name} has been deleted."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Delete Failed",
                        "Could not delete the character. It may have already been deleted."
                    )
            except Exception as e:
                self.app_context.rollback()
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while deleting the character:\n{str(e)}"
                )
    
    def _generate_embedding(self, text: str) -> Optional[list]:
        """Generate embedding vector for text using nomic-embed-text via Ollama."""
        from nico.infrastructure.database.settings import Settings
        settings = Settings()
        try:
            import requests
            response = requests.post(
                'http://127.0.0.1:11434/api/embeddings',
                json={
                    'model': settings.EMBEDDING_MODEL,
                    'prompt': text
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get('embedding')
        except Exception as e:
            print(f"Warning: Failed to generate embedding: {e}")
            return None
    
    def _on_dimension_preset_changed(self, preset_text: str) -> None:
        """Handle dimension preset selection.
        
        Uses SDXL-trained resolutions for optimal quality.
        """
        presets = {
            "Square 1024×1024": (1024, 1024),
            "Portrait 832×1216": (832, 1216),
            "Portrait 896×1152": (896, 1152),
            "Landscape 1216×832": (1216, 832),
            "Landscape 1152×896": (1152, 896),
            "Wide 1344×768": (1344, 768),
            "Wide 1536×640": (1536, 640),
            "Tall 768×1344": (768, 1344),
            "Tall 640×1536": (640, 1536),
        }
        
        if preset_text == "Custom":
            # Enable custom dimension spinboxes
            self.width_spin.setEnabled(True)
            self.height_spin.setEnabled(True)
        elif preset_text in presets:
            # Disable spinboxes and set preset values
            self.width_spin.setEnabled(False)
            self.height_spin.setEnabled(False)
            width, height = presets[preset_text]
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)
    
    def _build_image_prompt(self) -> str:
        """Build a comprehensive natural language prompt from character attributes."""
        if not self.current_character:
            return ""
        
        char = self.current_character
        prompt_parts = []
        
        # Start with physical description if available
        physical_description = self.physical_value.toPlainText().strip()
        if physical_description:
            prompt_parts.append(physical_description)
        
        # Add demographic information
        demographic_parts = []
        
        # Gender
        if char.gender:
            demographic_parts.append(char.gender.lower())
        
        # Age (calculate from date of birth if available)
        if char.date_of_birth:
            from datetime import date
            today = date.today()
            age = today.year - char.date_of_birth.year - (
                (today.month, today.day) < (char.date_of_birth.month, char.date_of_birth.day)
            )
            demographic_parts.append(f"{age} years old")
        
        # Ethnicity and nationality
        if char.ethnicity and char.nationality:
            demographic_parts.append(f"{char.ethnicity} {char.nationality}")
        elif char.ethnicity:
            demographic_parts.append(char.ethnicity)
        elif char.nationality:
            demographic_parts.append(char.nationality)
        
        # Tribe or clan
        if char.tribe_or_clan:
            demographic_parts.append(f"of the {char.tribe_or_clan}")
        
        if demographic_parts:
            prompt_parts.append("A " + " ".join(demographic_parts) + " person.")
        
        # Add occupation context
        if char.occupation:
            prompt_parts.append(f"Works as a {char.occupation}.")
        
        return " ".join(prompt_parts)
    
    def _on_generate_image(self) -> None:
        """Generate character portrait using ComfyUI."""
        if not self.current_character:
            return
        
        # Build comprehensive prompt from character attributes
        full_prompt = self._build_image_prompt()
        
        if not full_prompt:
            QMessageBox.warning(
                self,
                "No Description",
                "Please add a physical description before generating a portrait."
            )
            return
        
        # Disable controls while generating
        self.generate_image_btn.setEnabled(False)
        self.upload_image_btn.setEnabled(False)
        self.clear_image_btn.setEnabled(False)
        self.dimension_preset.setEnabled(False)
        self.seed_input.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.show()
        
        # Get dimensions and seed
        width = self.width_spin.value()
        height = self.height_spin.value()
        seed_text = self.seed_input.text().strip()
        seed = int(seed_text) if seed_text.isdigit() else None
        
        # Get project directory (where Nico is running from)
        # Images will be saved to <project_root>/media/portraits/
        project_path = Path.cwd()
        
        # Store prompt for later use in completion handler
        self._current_prompt = full_prompt
        
        # Create worker and thread
        self.worker = ImageGenerationWorker(full_prompt, project_path, width, height, seed)
        self.thread = QThread()
        
        # Move worker to thread
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_image_generated)
        self.worker.error.connect(self._on_image_generation_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start the thread
        self.thread.start()
    
    def _on_image_generated(self, image_path) -> None:
        """Handle successful image generation (called on main thread)."""
        # Re-enable controls
        self.generate_image_btn.setEnabled(True)
        self.upload_image_btn.setEnabled(True)
        self.clear_image_btn.setEnabled(True)
        self.dimension_preset.setEnabled(True)
        self.seed_input.setEnabled(True)
        
        # Hide progress bar
        self.progress_bar.hide()
        
        if image_path and image_path.exists():
            # Load and display the image
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                # Calculate dimensions: scale the larger dimension to max, other proportionally
                img_width = pixmap.width()
                img_height = pixmap.height()
                max_size = 512
                
                if img_width >= img_height:
                    # Width is larger - scale to max width
                    display_width = max_size
                    display_height = int((img_height / img_width) * max_size)
                else:
                    # Height is larger - scale to max height
                    display_height = max_size
                    display_width = int((img_width / img_height) * max_size)
                
                self.image_label.setMinimumSize(display_width, display_height)
                self.image_label.setMaximumSize(display_width, display_height)
                scaled_pixmap = pixmap.scaled(
                    display_width, display_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                
                # Save image path and prompt with embedding to character
                if self.current_character:
                    # Delete old image file if it exists
                    if self.current_character.image_path:
                        old_image = Path(self.current_character.image_path)
                        if old_image.exists():
                            try:
                                old_image.unlink()
                                print(f"Deleted old image: {old_image}")
                            except Exception as e:
                                print(f"Warning: Could not delete old image: {e}")
                    
                    # Generate embedding for the prompt
                    embedding = self._generate_embedding(self._current_prompt)
                    
                    self.app_context.character_service.update_character(
                        self.current_character.id,
                        image_path=str(image_path),
                        image_prompt=self._current_prompt,
                        image_embedding=embedding
                    )
                    self.app_context.commit()  # Commit the transaction
                    # Refresh character object to get updated data
                    self.current_character = self.app_context.character_service.get_character(
                        self.current_character.id
                    )
            else:
                QMessageBox.warning(self, "Error", "Failed to load generated image")
        else:
            QMessageBox.warning(
                self,
                "Generation Failed",
                "ComfyUI did not return an image. Check the console for details.\n\n"
                "Make sure ComfyUI is running at http://127.0.0.1:8188"
            )
    
    def _on_image_generation_failed(self, error_msg: str) -> None:
        """Handle failed image generation (called on main thread)."""
        # Re-enable controls
        self.generate_image_btn.setEnabled(True)
        self.upload_image_btn.setEnabled(True)
        self.clear_image_btn.setEnabled(True)
        self.dimension_preset.setEnabled(True)
        self.seed_input.setEnabled(True)
        
        # Hide progress bar
        self.progress_bar.hide()
        
        QMessageBox.critical(
            self,
            "Generation Error",
            f"Failed to generate portrait:\n\n{error_msg}\n\n"
            "Make sure ComfyUI is running at http://127.0.0.1:8188"
        )
    
    def _on_upload_image(self) -> None:
        """Upload a custom character image."""
        if not self.current_character:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Character Portrait",
            "",
            "Image Files (*.png *.jpg *.jpeg *.webp)"
        )
        
        if file_path:
            # Load and display the image
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Calculate dimensions: scale the larger dimension to max, other proportionally
                img_width = pixmap.width()
                img_height = pixmap.height()
                max_size = 512
                
                if img_width >= img_height:
                    # Width is larger - scale to max width
                    display_width = max_size
                    display_height = int((img_height / img_width) * max_size)
                else:
                    # Height is larger - scale to max height
                    display_height = max_size
                    display_width = int((img_width / img_height) * max_size)
                
                self.image_label.setMinimumSize(display_width, display_height)
                self.image_label.setMaximumSize(display_width, display_height)
                scaled_pixmap = pixmap.scaled(
                    display_width, display_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                
                # Save image path to character
                if self.current_character:
                    self.app_context.character_service.update_character(
                        self.current_character.id,
                        image_path=file_path
                    )
                    self.app_context.commit()
                    self.current_character = self.app_context.character_service.get_character(
                        self.current_character.id
                    )
            else:
                QMessageBox.warning(self, "Error", "Failed to load image")
    def _on_clear_image(self) -> None:
        """Clear the character's portrait."""
        if not self.current_character:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Clear Portrait",
            "Remove the current portrait from this character?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Delete the image file if it exists
        if self.current_character.image_path:
            image_file = Path(self.current_character.image_path)
            if image_file.exists():
                try:
                    image_file.unlink()
                    print(f"Deleted image: {image_file}")
                except Exception as e:
                    print(f"Warning: Could not delete image file: {e}")
        
        # Clear the image from database
        self.app_context.character_service.update_character(
            self.current_character.id,
            image_path=None,
            image_prompt=None,
            image_embedding=None
        )
        self.app_context.commit()
        
        # Refresh character and UI
        self.current_character = self.app_context.character_service.get_character(
            self.current_character.id
        )
        self.image_label.clear()
        self.image_label.setText("No portrait yet\n\nClick 'Generate'\nto create one")
    
    def _on_portrait_clicked(self, event) -> None:
        """Handle click on portrait image to view in system viewer."""
        if not self.current_character or not self.current_character.image_path:
            return
        
        from pathlib import Path
        image_path = Path(self.current_character.image_path)
        
        if not image_path.exists():
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Portrait file not found:\n{image_path}"
            )
            return
        
        # Open with system default application
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(image_path.absolute())))
