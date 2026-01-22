"""Character creation and editing dialog."""
from typing import Optional
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QDateEdit,
    QCheckBox,
    QPushButton,
    QTabWidget,
    QWidget,
    QLabel,
    QScrollArea,
    QGroupBox,
)
from PySide6.QtCore import QDate

from nico.domain.models import Character
from nico.application.context import get_app_context


class CharacterDialog(QDialog):
    """Dialog for creating or editing a character."""
    
    def __init__(self, project_id: int, character: Optional[Character] = None, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.character = character
        self.is_editing = character is not None
        self.app_context = get_app_context()
        
        self.setWindowTitle("Edit Character" if self.is_editing else "New Character")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self._setup_ui()
        if self.is_editing:
            self._load_character_data()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Tab widget for organizing fields
        tabs = QTabWidget()
        
        # Basic Info Tab
        tabs.addTab(self._create_basic_tab(), "Basic Info")
        
        # Identity Tab
        tabs.addTab(self._create_identity_tab(), "Identity")
        
        # Life Tab
        tabs.addTab(self._create_life_tab(), "Life Details")
        
        # Psychology Tab
        tabs.addTab(self._create_psychology_tab(), "Psychology")
        
        layout.addWidget(tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_character)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _create_basic_tab(self) -> QWidget:
        """Create the basic info tab."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QFormLayout()
        
        # Name fields
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Mr., Ms., Dr., etc.")
        layout.addRow("Title:", self.title_edit)
        
        self.honorific_edit = QLineEdit()
        self.honorific_edit.setPlaceholderText("Sir, Dame, Lord, etc.")
        layout.addRow("Honorific:", self.honorific_edit)
        
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Given name")
        layout.addRow("First Name:", self.first_name_edit)
        
        self.middle_names_edit = QLineEdit()
        self.middle_names_edit.setPlaceholderText("Middle name(s)")
        layout.addRow("Middle Names:", self.middle_names_edit)
        
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Family name")
        layout.addRow("Last Name:", self.last_name_edit)
        
        self.nickname_edit = QLineEdit()
        self.nickname_edit.setPlaceholderText("Nickname or preferred name")
        layout.addRow("Nickname:", self.nickname_edit)
        
        # Physical description
        self.physical_edit = QTextEdit()
        self.physical_edit.setPlaceholderText("Physical appearance, distinguishing features...")
        self.physical_edit.setMaximumHeight(100)
        layout.addRow("Physical Description:", self.physical_edit)
        
        # AI exclusion
        self.exclude_ai_checkbox = QCheckBox("Exclude from AI suggestions")
        layout.addRow("", self.exclude_ai_checkbox)
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)
        return widget
    
    def _create_identity_tab(self) -> QWidget:
        """Create the identity tab."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QFormLayout()
        
        self.gender_edit = QLineEdit()
        self.gender_edit.setPlaceholderText("Gender identity")
        layout.addRow("Gender:", self.gender_edit)
        
        self.sex_edit = QLineEdit()
        self.sex_edit.setPlaceholderText("Biological sex")
        layout.addRow("Sex:", self.sex_edit)
        
        self.ethnicity_edit = QLineEdit()
        self.ethnicity_edit.setPlaceholderText("Ethnic background")
        layout.addRow("Ethnicity:", self.ethnicity_edit)
        
        self.race_edit = QLineEdit()
        self.race_edit.setPlaceholderText("Racial identity")
        layout.addRow("Race:", self.race_edit)
        
        self.tribe_edit = QLineEdit()
        self.tribe_edit.setPlaceholderText("Tribal or clan affiliation")
        layout.addRow("Tribe/Clan:", self.tribe_edit)
        
        self.nationality_edit = QLineEdit()
        self.nationality_edit.setPlaceholderText("National origin")
        layout.addRow("Nationality:", self.nationality_edit)
        
        self.religion_edit = QLineEdit()
        self.religion_edit.setPlaceholderText("Religious affiliation")
        layout.addRow("Religion:", self.religion_edit)
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)
        return widget
    
    def _create_life_tab(self) -> QWidget:
        """Create the life details tab."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QFormLayout()
        
        self.occupation_edit = QLineEdit()
        self.occupation_edit.setPlaceholderText("Current occupation")
        layout.addRow("Occupation:", self.occupation_edit)
        
        self.education_edit = QLineEdit()
        self.education_edit.setPlaceholderText("Educational background")
        layout.addRow("Education:", self.education_edit)
        
        self.marital_status_edit = QLineEdit()
        self.marital_status_edit.setPlaceholderText("Single, married, divorced, etc.")
        layout.addRow("Marital Status:", self.marital_status_edit)
        
        self.has_children_checkbox = QCheckBox("Has children")
        layout.addRow("Children:", self.has_children_checkbox)
        
        # Dates
        self.dob_edit = QDateEdit()
        self.dob_edit.setCalendarPopup(True)
        self.dob_edit.setSpecialValueText("Not set")
        self.dob_edit.setDate(QDate(2000, 1, 1))
        layout.addRow("Date of Birth:", self.dob_edit)
        
        self.dod_edit = QDateEdit()
        self.dod_edit.setCalendarPopup(True)
        self.dod_edit.setSpecialValueText("Not set")
        self.dod_edit.setDate(QDate(2000, 1, 1))
        layout.addRow("Date of Death:", self.dod_edit)
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)
        return widget
    
    def _create_psychology_tab(self) -> QWidget:
        """Create the psychology tab."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QFormLayout()
        
        self.myers_briggs_edit = QLineEdit()
        self.myers_briggs_edit.setPlaceholderText("e.g., INTJ, ENFP")
        self.myers_briggs_edit.setMaxLength(4)
        layout.addRow("Myers-Briggs:", self.myers_briggs_edit)
        
        self.enneagram_edit = QLineEdit()
        self.enneagram_edit.setPlaceholderText("e.g., Type 4, 7w8")
        layout.addRow("Enneagram:", self.enneagram_edit)
        
        self.wounds_edit = QTextEdit()
        self.wounds_edit.setPlaceholderText("Emotional wounds, traumas, fears...")
        self.wounds_edit.setMaximumHeight(100)
        layout.addRow("Wounds:", self.wounds_edit)
        
        # Note about traits
        info_label = QLabel(
            "Note: Custom trait sliders (brave, loyal, etc.) can be added "
            "via the advanced editor in future versions."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        layout.addRow("", info_label)
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)
        return widget
    
    def _load_character_data(self) -> None:
        """Load existing character data into the form."""
        if not self.character:
            return
        
        # Basic info
        self.title_edit.setText(self.character.title or "")
        self.honorific_edit.setText(self.character.honorific or "")
        self.first_name_edit.setText(self.character.first_name or "")
        self.middle_names_edit.setText(self.character.middle_names or "")
        self.last_name_edit.setText(self.character.last_name or "")
        self.nickname_edit.setText(self.character.nickname or "")
        self.physical_edit.setPlainText(self.character.physical_description or "")
        self.exclude_ai_checkbox.setChecked(self.character.exclude_from_ai)
        
        # Identity
        self.gender_edit.setText(self.character.gender or "")
        self.sex_edit.setText(self.character.sex or "")
        self.ethnicity_edit.setText(self.character.ethnicity or "")
        self.race_edit.setText(self.character.race or "")
        self.tribe_edit.setText(self.character.tribe_or_clan or "")
        self.nationality_edit.setText(self.character.nationality or "")
        self.religion_edit.setText(self.character.religion or "")
        
        # Life
        self.occupation_edit.setText(self.character.occupation or "")
        self.education_edit.setText(self.character.education or "")
        self.marital_status_edit.setText(self.character.marital_status or "")
        if self.character.has_children is not None:
            self.has_children_checkbox.setChecked(self.character.has_children)
        
        if self.character.date_of_birth:
            self.dob_edit.setDate(QDate(
                self.character.date_of_birth.year,
                self.character.date_of_birth.month,
                self.character.date_of_birth.day
            ))
        
        if self.character.date_of_death:
            self.dod_edit.setDate(QDate(
                self.character.date_of_death.year,
                self.character.date_of_death.month,
                self.character.date_of_death.day
            ))
        
        # Psychology
        self.myers_briggs_edit.setText(self.character.myers_briggs or "")
        self.enneagram_edit.setText(self.character.enneagram or "")
        self.wounds_edit.setPlainText(self.character.wounds or "")
    
    def _save_character(self) -> None:
        """Save the character to database."""
        # Collect data
        data = {
            "title": self.title_edit.text() or None,
            "honorific": self.honorific_edit.text() or None,
            "first_name": self.first_name_edit.text() or None,
            "middle_names": self.middle_names_edit.text() or None,
            "last_name": self.last_name_edit.text() or None,
            "nickname": self.nickname_edit.text() or None,
            "physical_description": self.physical_edit.toPlainText() or None,
            "gender": self.gender_edit.text() or None,
            "sex": self.sex_edit.text() or None,
            "ethnicity": self.ethnicity_edit.text() or None,
            "race": self.race_edit.text() or None,
            "tribe_or_clan": self.tribe_edit.text() or None,
            "nationality": self.nationality_edit.text() or None,
            "religion": self.religion_edit.text() or None,
            "occupation": self.occupation_edit.text() or None,
            "education": self.education_edit.text() or None,
            "marital_status": self.marital_status_edit.text() or None,
            "has_children": self.has_children_checkbox.isChecked() if self.has_children_checkbox.isChecked() else None,
            "myers_briggs": self.myers_briggs_edit.text() or None,
            "enneagram": self.enneagram_edit.text() or None,
            "wounds": self.wounds_edit.toPlainText() or None,
            "exclude_from_ai": self.exclude_ai_checkbox.isChecked(),
        }
        
        # Handle dates
        dob_date = self.dob_edit.date()
        if dob_date and dob_date != QDate(2000, 1, 1):
            data["date_of_birth"] = date(dob_date.year(), dob_date.month(), dob_date.day())
        
        dod_date = self.dod_edit.date()
        if dod_date and dod_date != QDate(2000, 1, 1):
            data["date_of_death"] = date(dod_date.year(), dod_date.month(), dod_date.day())
        
        try:
            if self.is_editing:
                # Update existing character
                self.app_context.character_service.update_character(
                    self.character.id,
                    **data
                )
            else:
                # Create new character
                self.app_context.character_service.create_character(
                    self.project_id,
                    **data
                )
            
            self.app_context.commit()
            self.accept()
        except Exception as e:
            self.app_context.rollback()
            # TODO: Show error dialog
            print(f"Error saving character: {e}")
