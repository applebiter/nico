"""Location creation and editing dialog."""
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
    QTabWidget,
    QWidget,
    QLabel,
    QScrollArea,
)

from nico.domain.models import Location
from nico.application.context import get_app_context


class LocationDialog(QDialog):
    """Dialog for creating or editing a location."""
    
    def __init__(self, project_id: int, location: Optional[Location] = None, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.location = location
        self.is_editing = location is not None
        self.app_context = get_app_context()
        
        self.setWindowTitle("Edit Location" if self.is_editing else "New Location")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self._setup_ui()
        if self.is_editing:
            self._load_location_data()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Tab widget for organizing fields
        tabs = QTabWidget()
        
        # Basic Info Tab
        tabs.addTab(self._create_basic_tab(), "Basic Info")
        
        # Details Tab
        tabs.addTab(self._create_details_tab(), "Details")
        
        # Culture & Society Tab
        tabs.addTab(self._create_society_tab(), "Culture & Society")
        
        layout.addWidget(tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_location)
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
        
        # Name (required)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Location name (required)")
        layout.addRow("Name:*", self.name_edit)
        
        # Type
        self.type_edit = QLineEdit()
        self.type_edit.setPlaceholderText("City, building, planet, forest, etc.")
        layout.addRow("Type:", self.type_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("General description of the location...")
        self.description_edit.setMaximumHeight(120)
        layout.addRow("Description:", self.description_edit)
        
        # Atmosphere
        self.atmosphere_edit = QTextEdit()
        self.atmosphere_edit.setPlaceholderText("Mood, feeling, ambiance of the location...")
        self.atmosphere_edit.setMaximumHeight(80)
        layout.addRow("Atmosphere:", self.atmosphere_edit)
        
        # AI exclusion
        self.exclude_ai_checkbox = QCheckBox("Exclude from AI suggestions")
        layout.addRow("", self.exclude_ai_checkbox)
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)
        return widget
    
    def _create_details_tab(self) -> QWidget:
        """Create the details tab."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QFormLayout()
        
        # Geography
        self.geography_edit = QTextEdit()
        self.geography_edit.setPlaceholderText("Physical features, terrain, landmarks...")
        self.geography_edit.setMaximumHeight(100)
        layout.addRow("Geography:", self.geography_edit)
        
        # Climate
        self.climate_edit = QTextEdit()
        self.climate_edit.setPlaceholderText("Weather patterns, seasons, temperature...")
        self.climate_edit.setMaximumHeight(80)
        layout.addRow("Climate:", self.climate_edit)
        
        # History
        self.history_edit = QTextEdit()
        self.history_edit.setPlaceholderText("Historical background, founding, major events...")
        self.history_edit.setMaximumHeight(100)
        layout.addRow("History:", self.history_edit)
        
        # Population
        self.population_edit = QTextEdit()
        self.population_edit.setPlaceholderText("Population size, demographics, inhabitants...")
        self.population_edit.setMaximumHeight(80)
        layout.addRow("Population:", self.population_edit)
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)
        return widget
    
    def _create_society_tab(self) -> QWidget:
        """Create the society tab."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QFormLayout()
        
        # Culture
        self.culture_edit = QTextEdit()
        self.culture_edit.setPlaceholderText("Cultural aspects, traditions, customs...")
        self.culture_edit.setMaximumHeight(100)
        layout.addRow("Culture:", self.culture_edit)
        
        # Economy
        self.economy_edit = QTextEdit()
        self.economy_edit.setPlaceholderText("Economic system, trade, resources, industries...")
        self.economy_edit.setMaximumHeight(100)
        layout.addRow("Economy:", self.economy_edit)
        
        # Government
        self.government_edit = QTextEdit()
        self.government_edit.setPlaceholderText("Political system, leadership, laws...")
        self.government_edit.setMaximumHeight(100)
        layout.addRow("Government:", self.government_edit)
        
        # Note about attributes
        info_label = QLabel(
            "Note: Custom attribute sliders (danger level, wealth, etc.) can be added "
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
    
    def _load_location_data(self) -> None:
        """Load existing location data into the form."""
        if not self.location:
            return
        
        # Basic info
        self.name_edit.setText(self.location.name)
        self.type_edit.setText(self.location.location_type or "")
        self.description_edit.setPlainText(self.location.description or "")
        self.atmosphere_edit.setPlainText(self.location.atmosphere or "")
        self.exclude_ai_checkbox.setChecked(self.location.exclude_from_ai)
        
        # Details
        self.geography_edit.setPlainText(self.location.geography or "")
        self.climate_edit.setPlainText(self.location.climate or "")
        self.history_edit.setPlainText(self.location.history or "")
        self.population_edit.setPlainText(self.location.population or "")
        
        # Society
        self.culture_edit.setPlainText(self.location.culture or "")
        self.economy_edit.setPlainText(self.location.economy or "")
        self.government_edit.setPlainText(self.location.government or "")
    
    def _save_location(self) -> None:
        """Save the location to database."""
        # Validate required fields
        name = self.name_edit.text().strip()
        if not name:
            # TODO: Show error dialog
            print("Location name is required")
            return
        
        # Collect data
        data = {
            "name": name,
            "location_type": self.type_edit.text() or None,
            "description": self.description_edit.toPlainText() or None,
            "atmosphere": self.atmosphere_edit.toPlainText() or None,
            "geography": self.geography_edit.toPlainText() or None,
            "climate": self.climate_edit.toPlainText() or None,
            "history": self.history_edit.toPlainText() or None,
            "population": self.population_edit.toPlainText() or None,
            "culture": self.culture_edit.toPlainText() or None,
            "economy": self.economy_edit.toPlainText() or None,
            "government": self.government_edit.toPlainText() or None,
            "exclude_from_ai": self.exclude_ai_checkbox.isChecked(),
        }
        
        try:
            if self.is_editing:
                # Update existing location
                self.app_context.location_service.update_location(
                    self.location.id,
                    **data
                )
            else:
                # Create new location
                self.app_context.location_service.create_location(
                    self.project_id,
                    **data
                )
            
            self.app_context.commit()
            self.accept()
        except Exception as e:
            self.app_context.rollback()
            # TODO: Show error dialog
            print(f"Error saving location: {e}")
