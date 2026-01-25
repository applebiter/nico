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

from nico.domain.models import Character, WorldBuildingTable
from nico.application.context import get_app_context
from nico.presentation.widgets.searchable_combo import SearchableComboBox
from nico.presentation.widgets.async_search_combo import AsyncSearchComboBox


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
        
        # Cache for world-building tables
        self._table_cache = {}
        
        self._setup_ui()
        if self.is_editing:
            self._load_character_data()
    
    def _get_table_items(self, table_name: str) -> list[str]:
        """Get items from a world-building table (with caching).
        
        For CSV-imported global tables (names, occupations, etc.), we query
        without project_id filter to find tables shared across all projects.
        """
        if table_name in self._table_cache:
            return self._table_cache[table_name]
        
        # Global CSV tables that should be available to all projects
        global_tables = [
            "generator-names.male",
            "generator-names.female",
            "generator-names.surnames",
            "generator-names.city_of_origin",
            "characters",  # occupations
            "character.types",
            "character.motivations",
            "character.wounds",
            "random_trait_generator.col1",
            "personality.myers_briggs",
            "personality.enneagram",
        ]
        
        if table_name in global_tables:
            # Query any instance of this table (first match)
            table = self.app_context._session.query(WorldBuildingTable).filter_by(
                table_name=table_name
            ).first()
        else:
            # Project-specific table
            table = self.app_context._session.query(WorldBuildingTable).filter_by(
                project_id=self.project_id,
                table_name=table_name
            ).first()
        
        items = table.items if table else []
        
        # Format names to title case (names tables often have ALL CAPS)
        name_tables = [
            "generator-names.male",
            "generator-names.female",
            "generator-names.surnames",
            "generator-names.city_of_origin",
        ]
        
        if table_name in name_tables:
            items = [item.title() for item in items]
        
        self._table_cache[table_name] = items
        return items
    
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
        
        # First name with dropdown from generator-names tables
        first_name_layout = QHBoxLayout()
        self.first_name_edit = SearchableComboBox()
        self.first_name_edit.setEditable(True)
        male_names = self._get_table_items("generator-names.male")
        female_names = self._get_table_items("generator-names.female")
        all_first_names = sorted(set(male_names + female_names), key=str.lower)
        if all_first_names:
            self.first_name_edit.setItems(all_first_names, sort=False)
        self.first_name_edit.lineEdit().setPlaceholderText("Given name (type or select)")
        
        random_first_btn = QPushButton("🎲")
        random_first_btn.setMaximumWidth(40)
        random_first_btn.setToolTip("Random first name")
        random_first_btn.clicked.connect(lambda: self._randomize_combo(self.first_name_edit))
        
        first_name_layout.addWidget(self.first_name_edit)
        first_name_layout.addWidget(random_first_btn)
        layout.addRow("First Name:", first_name_layout)
        
        self.middle_names_edit = QLineEdit()
        self.middle_names_edit.setPlaceholderText("Middle name(s)")
        layout.addRow("Middle Names:", self.middle_names_edit)
        
        # Last name with dropdown from surnames
        last_name_layout = QHBoxLayout()
        self.last_name_edit = SearchableComboBox()
        self.last_name_edit.setEditable(True)
        surnames = self._get_table_items("generator-names.surnames")
        if surnames:
            self.last_name_edit.setItems(surnames)
        self.last_name_edit.lineEdit().setPlaceholderText("Family name (type or select)")
        
        random_last_btn = QPushButton("🎲")
        random_last_btn.setMaximumWidth(40)
        random_last_btn.setToolTip("Random surname")
        random_last_btn.clicked.connect(lambda: self._randomize_combo(self.last_name_edit))
        
        last_name_layout.addWidget(self.last_name_edit)
        last_name_layout.addWidget(random_last_btn)
        layout.addRow("Last Name:", last_name_layout)
        
        self.nickname_edit = QLineEdit()
        self.nickname_edit.setPlaceholderText("Nickname or preferred name")
        layout.addRow("Nickname:", self.nickname_edit)
        
        # Physical description
        self.physical_edit = QTextEdit()
        self.physical_edit.setAcceptRichText(False)
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
        
        # Hometown/Origin with city dropdown
        hometown_layout = QHBoxLayout()
        self.hometown_edit = SearchableComboBox()
        self.hometown_edit.setEditable(True)
        cities = self._get_table_items("generator-names.city_of_origin")
        if cities:
            self.hometown_edit.setItems(cities)
        self.hometown_edit.lineEdit().setPlaceholderText("Hometown or place of origin (601 cities)")
        
        random_city_btn = QPushButton("🎲")
        random_city_btn.setMaximumWidth(40)
        random_city_btn.setToolTip("Random city")
        random_city_btn.clicked.connect(lambda: self._randomize_combo(self.hometown_edit))
        
        hometown_layout.addWidget(self.hometown_edit)
        hometown_layout.addWidget(random_city_btn)
        layout.addRow("Hometown:", hometown_layout)
        
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
        
        # Occupation with async search (5,798 options!)
        occupation_layout = QHBoxLayout()
        self.occupation_edit = AsyncSearchComboBox()
        self.occupation_edit.set_search_function(self._search_occupations)
        # Load all items for random selection (but don't add to combo)
        all_occupations = self._get_table_items("characters")
        self.occupation_edit.set_all_items(all_occupations)
        self.occupation_edit.lineEdit().setPlaceholderText("Type to search 5,798 occupations...")
        
        random_occ_btn = QPushButton("🎲")
        random_occ_btn.setMaximumWidth(40)
        random_occ_btn.setToolTip("Random occupation")
        random_occ_btn.clicked.connect(self._randomize_occupation)
        
        occupation_layout.addWidget(self.occupation_edit)
        occupation_layout.addWidget(random_occ_btn)
        layout.addRow("Occupation:", occupation_layout)
        
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
        
        # Character Type (Reformer, Helper, Achiever, etc.)
        char_type_layout = QHBoxLayout()
        self.character_type_edit = SearchableComboBox()
        self.character_type_edit.setEditable(True)
        char_types = self._get_table_items("character.types")
        if char_types:
            self.character_type_edit.setItems(char_types)
        self.character_type_edit.lineEdit().setPlaceholderText("Character archetype (9 types)")
        
        random_type_btn = QPushButton("🎲")
        random_type_btn.setMaximumWidth(40)
        random_type_btn.setToolTip("Random character type")
        random_type_btn.clicked.connect(lambda: self._randomize_combo(self.character_type_edit))
        
        char_type_layout.addWidget(self.character_type_edit)
        char_type_layout.addWidget(random_type_btn)
        layout.addRow("Character Type:", char_type_layout)
        
        # Motivation
        motivation_layout = QHBoxLayout()
        self.motivation_edit = SearchableComboBox()
        self.motivation_edit.setEditable(True)
        motivations = self._get_table_items("character.motivations")
        if motivations:
            self.motivation_edit.setItems(motivations)
        self.motivation_edit.lineEdit().setPlaceholderText("Core motivation (23 options)")
        
        random_motivation_btn = QPushButton("🎲")
        random_motivation_btn.setMaximumWidth(40)
        random_motivation_btn.setToolTip("Random motivation")
        random_motivation_btn.clicked.connect(lambda: self._randomize_combo(self.motivation_edit))
        
        motivation_layout.addWidget(self.motivation_edit)
        motivation_layout.addWidget(random_motivation_btn)
        layout.addRow("Motivation:", motivation_layout)
        
        # Personality Trait
        trait_layout = QHBoxLayout()
        self.trait_edit = SearchableComboBox()
        self.trait_edit.setEditable(True)
        traits = self._get_table_items("random_trait_generator.col1")
        if traits:
            self.trait_edit.setItems(traits)
        self.trait_edit.lineEdit().setPlaceholderText("Dominant personality trait (15 options)")
        
        random_trait_btn = QPushButton("🎲")
        random_trait_btn.setMaximumWidth(40)
        random_trait_btn.setToolTip("Random trait")
        random_trait_btn.clicked.connect(lambda: self._randomize_combo(self.trait_edit))
        
        trait_layout.addWidget(self.trait_edit)
        trait_layout.addWidget(random_trait_btn)
        layout.addRow("Personality Trait:", trait_layout)
        
        # Myers-Briggs Type (16 types)
        mb_layout = QHBoxLayout()
        self.myers_briggs_edit = SearchableComboBox()
        self.myers_briggs_edit.setEditable(True)
        mb_types = self._get_table_items("personality.myers_briggs")
        if mb_types:
            self.myers_briggs_edit.setItems(mb_types, sort=False)
        self.myers_briggs_edit.lineEdit().setPlaceholderText("Myers-Briggs type (16 options)")
        
        random_mb_btn = QPushButton("🎲")
        random_mb_btn.setMaximumWidth(40)
        random_mb_btn.setToolTip("Random Myers-Briggs type")
        random_mb_btn.clicked.connect(lambda: self._randomize_combo(self.myers_briggs_edit))
        
        mb_layout.addWidget(self.myers_briggs_edit)
        mb_layout.addWidget(random_mb_btn)
        layout.addRow("Myers-Briggs:", mb_layout)
        
        # Enneagram Type (9 types + wings)
        enneagram_layout = QHBoxLayout()
        self.enneagram_edit = SearchableComboBox()
        self.enneagram_edit.setEditable(True)
        enneagram_types = self._get_table_items("personality.enneagram")
        if enneagram_types:
            self.enneagram_edit.setItems(enneagram_types, sort=False)
        self.enneagram_edit.lineEdit().setPlaceholderText("Enneagram type (9 types + wings)")
        
        random_enneagram_btn = QPushButton("🎲")
        random_enneagram_btn.setMaximumWidth(40)
        random_enneagram_btn.setToolTip("Random Enneagram type")
        random_enneagram_btn.clicked.connect(lambda: self._randomize_combo(self.enneagram_edit))
        
        enneagram_layout.addWidget(self.enneagram_edit)
        enneagram_layout.addWidget(random_enneagram_btn)
        layout.addRow("Enneagram:", enneagram_layout)
        
        # Wounds with searchable dropdown (117 options!)
        wounds_layout = QHBoxLayout()
        self.wounds_edit = SearchableComboBox()
        self.wounds_edit.setEditable(True)
        wounds = self._get_table_items("character.wounds")
        if wounds:
            self.wounds_edit.setItems(wounds)
        self.wounds_edit.lineEdit().setPlaceholderText("Primary wound/trauma (117 options or type custom)")
        
        random_wounds_btn = QPushButton("🎲")
        random_wounds_btn.setMaximumWidth(40)
        random_wounds_btn.setToolTip("Random wound")
        random_wounds_btn.clicked.connect(lambda: self._randomize_combo(self.wounds_edit))
        
        wounds_layout.addWidget(self.wounds_edit)
        wounds_layout.addWidget(random_wounds_btn)
        layout.addRow("Primary Wound:", wounds_layout)
        
        # Additional wounds/notes
        self.wounds_notes_edit = QTextEdit()
        self.wounds_notes_edit.setAcceptRichText(False)
        self.wounds_notes_edit.setPlaceholderText("Additional wounds, traumas, fears, or notes...")
        self.wounds_notes_edit.setMaximumHeight(80)
        layout.addRow("Additional Notes:", self.wounds_notes_edit)
        
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
    
    def _search_occupations(self, query: str, limit: int) -> list[str]:
        """Search occupations by query string."""
        all_occupations = self._get_table_items("characters")
        
        if not query or len(query) < 2:
            return []
        
        # Case-insensitive search
        query_lower = query.lower()
        matches = [occ for occ in all_occupations if query_lower in occ.lower()]
        
        # Return limited results
        return matches[:limit]
    
    def _randomize_occupation(self) -> None:
        """Pick a random occupation."""
        random_item = self.occupation_edit.get_random_item()
        if random_item:
            self.occupation_edit.setText(random_item)
    
    def _randomize_combo(self, combo: SearchableComboBox) -> None:
        """Pick a random item from a combo box."""
        if combo.count() > 0:
            import random
            index = random.randint(0, combo.count() - 1)
            text = combo.itemText(index)
            combo.setEditText(text)
    
    def _load_character_data(self) -> None:
        """Load existing character data into the form."""
        if not self.character:
            return
        
        # Basic info
        self.title_edit.setText(self.character.title or "")
        self.honorific_edit.setText(self.character.honorific or "")
        
        # SearchableComboBox needs setText() method
        if hasattr(self.first_name_edit, 'setText'):
            self.first_name_edit.setText(self.character.first_name or "")
        else:
            self.first_name_edit.setCurrentText(self.character.first_name or "")
            
        self.middle_names_edit.setText(self.character.middle_names or "")
        
        if hasattr(self.last_name_edit, 'setText'):
            self.last_name_edit.setText(self.character.last_name or "")
        else:
            self.last_name_edit.setCurrentText(self.character.last_name or "")
            
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
        
        # Hometown from meta
        if self.character.meta and 'hometown' in self.character.meta:
            if hasattr(self.hometown_edit, 'setText'):
                self.hometown_edit.setText(self.character.meta['hometown'])
            else:
                self.hometown_edit.setCurrentText(self.character.meta['hometown'])
        
        # Life
        if hasattr(self.occupation_edit, 'setText'):
            self.occupation_edit.setText(self.character.occupation or "")
        else:
            self.occupation_edit.setCurrentText(self.character.occupation or "")
            
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
        # Load from psychological_profile
        psych_profile = self.character.psychological_profile or {}
        
        if psych_profile.get('character_type'):
            if hasattr(self.character_type_edit, 'setText'):
                self.character_type_edit.setText(psych_profile['character_type'])
            else:
                self.character_type_edit.setCurrentText(psych_profile['character_type'])
        
        if psych_profile.get('motivation'):
            if hasattr(self.motivation_edit, 'setText'):
                self.motivation_edit.setText(psych_profile['motivation'])
            else:
                self.motivation_edit.setCurrentText(psych_profile['motivation'])
        
        if psych_profile.get('trait'):
            if hasattr(self.trait_edit, 'setText'):
                self.trait_edit.setText(psych_profile['trait'])
            else:
                self.trait_edit.setCurrentText(psych_profile['trait'])
        
        self.myers_briggs_edit.setText(self.character.myers_briggs or "")
        self.enneagram_edit.setText(self.character.enneagram or "")
        
        # Wounds - primary wound from wounds field, notes from meta
        if self.character.wounds:
            if hasattr(self.wounds_edit, 'setText'):
                self.wounds_edit.setText(self.character.wounds)
            else:
                self.wounds_edit.setCurrentText(self.character.wounds)
        
        if self.character.meta and 'wounds_notes' in self.character.meta:
            self.wounds_notes_edit.setPlainText(self.character.meta['wounds_notes'])
    
    def _save_character(self) -> None:
        """Save the character to database."""
        # Helper to get text from either QLineEdit or SearchableComboBox
        def get_text(widget):
            if hasattr(widget, 'currentText'):
                return widget.currentText() or None
            return widget.text() or None
        
        # Collect data
        data = {
            "title": self.title_edit.text() or None,
            "honorific": self.honorific_edit.text() or None,
            "first_name": get_text(self.first_name_edit),
            "middle_names": self.middle_names_edit.text() or None,
            "last_name": get_text(self.last_name_edit),
            "nickname": self.nickname_edit.text() or None,
            "physical_description": self.physical_edit.toPlainText() or None,
            "gender": self.gender_edit.text() or None,
            "sex": self.sex_edit.text() or None,
            "ethnicity": self.ethnicity_edit.text() or None,
            "race": self.race_edit.text() or None,
            "tribe_or_clan": self.tribe_edit.text() or None,
            "nationality": self.nationality_edit.text() or None,
            "religion": self.religion_edit.text() or None,
            "occupation": get_text(self.occupation_edit),
            "education": self.education_edit.text() or None,
            "marital_status": self.marital_status_edit.text() or None,
            "has_children": self.has_children_checkbox.isChecked() if self.has_children_checkbox.isChecked() else None,
            "myers_briggs": self.myers_briggs_edit.text() or None,
            "enneagram": self.enneagram_edit.text() or None,
            "wounds": get_text(self.wounds_edit),  # Primary wound
            "exclude_from_ai": self.exclude_ai_checkbox.isChecked(),
        }
        
        # Build psychological_profile dict
        psychological_profile = {}
        char_type = get_text(self.character_type_edit)
        if char_type:
            psychological_profile['character_type'] = char_type
        
        motivation = get_text(self.motivation_edit)
        if motivation:
            psychological_profile['motivation'] = motivation
        
        trait = get_text(self.trait_edit)
        if trait:
            psychological_profile['trait'] = trait
        
        if psychological_profile:
            data['psychological_profile'] = psychological_profile
        
        # Build meta dict
        meta = {}
        hometown = get_text(self.hometown_edit)
        if hometown:
            meta['hometown'] = hometown
        
        wounds_notes = self.wounds_notes_edit.toPlainText()
        if wounds_notes:
            meta['wounds_notes'] = wounds_notes
        
        if meta:
            data['meta'] = meta
        
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
