"""Dialog for creating character relationships (interpersonal and symbolic)."""
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nico.domain.models import Character, Relationship, CharacterMotifRelationship, SymbolicMotif


class RelationshipDialog(QDialog):
    """Dialog for creating or editing character relationships.
    
    Supports two types of relationships:
    1. Character-to-Character (interpersonal relationships)
    2. Character-to-Motif (abstract/symbolic relationships)
    """
    
    def __init__(self, character: Character, project_id: int, 
                 available_characters: list[Character],
                 available_motifs: list[SymbolicMotif],
                 edit_relationship: Optional[Relationship | CharacterMotifRelationship] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.character = character
        self.project_id = project_id
        self.available_characters = available_characters
        self.available_motifs = available_motifs
        self.edit_relationship = edit_relationship
        self.is_editing = edit_relationship is not None
        
        self.relationship_data = None
        self._setup_ui()
        
        # Load existing data if editing
        if self.is_editing:
            self._load_relationship_data()
        
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        title = "Edit Relationship" if self.is_editing else "Add Relationship"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Character name display
        char_name = self._get_character_display_name(self.character)
        header = QLabel(f"<h3>Add Relationship for {char_name}</h3>")
        layout.addWidget(header)
        
        # Relationship type selection
        type_group = QWidget()
        type_layout = QVBoxLayout()
        type_layout.setContentsMargins(0, 0, 0, 0)
        
        type_label = QLabel("<b>Relationship Type:</b>")
        type_layout.addWidget(type_label)
        
        self.type_button_group = QButtonGroup()
        
        self.interpersonal_radio = QRadioButton("Interpersonal (with another character)")
        self.interpersonal_radio.setChecked(True)
        self.type_button_group.addButton(self.interpersonal_radio, 0)
        type_layout.addWidget(self.interpersonal_radio)
        
        self.symbolic_radio = QRadioButton("Symbolic (with abstract concept/motif)")
        self.type_button_group.addButton(self.symbolic_radio, 1)
        type_layout.addWidget(self.symbolic_radio)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Stacked forms for different relationship types
        self.interpersonal_form = self._create_interpersonal_form()
        self.symbolic_form = self._create_symbolic_form()
        
        layout.addWidget(self.interpersonal_form)
        layout.addWidget(self.symbolic_form)
        
        # Initially show interpersonal form
        self.symbolic_form.hide()
        
        # Connect radio buttons to switch forms
        self.interpersonal_radio.toggled.connect(self._on_type_changed)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def _create_interpersonal_form(self) -> QWidget:
        """Create form for interpersonal relationships."""
        widget = QWidget()
        layout = QFormLayout()
        
        # Character selection
        self.character_combo = QComboBox()
        for char in self.available_characters:
            if char.id != self.character.id:  # Don't include self
                display_name = self._get_character_display_name(char)
                self.character_combo.addItem(display_name, char.id)
        layout.addRow("Character:", self.character_combo)
        
        # Relationship type
        self.rel_type_input = QLineEdit()
        self.rel_type_input.setPlaceholderText("e.g., sibling, spouse, enemy, mentor")
        layout.addRow("Relationship Type:", self.rel_type_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setAcceptRichText(False)
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Describe the relationship...")
        layout.addRow("Description:", self.description_input)
        
        # Attributes/sliders section
        attributes_label = QLabel("<b>Relationship Dynamics:</b>")
        layout.addRow(attributes_label)
        
        self.interpersonal_sliders = {}
        for attr in ["trust", "affection", "respect", "tension"]:
            slider_widget = self._create_slider_row(attr)
            layout.addRow(f"  {attr.capitalize()}:", slider_widget)
            self.interpersonal_sliders[attr] = slider_widget
        
        # Status and timeline
        self.status_input = QLineEdit()
        self.status_input.setPlaceholderText("e.g., active, estranged, deceased")
        layout.addRow("Status:", self.status_input)
        
        self.began_at_input = QLineEdit()
        self.began_at_input.setPlaceholderText("e.g., childhood, 2020, Act 1")
        layout.addRow("Began At:", self.began_at_input)
        
        widget.setLayout(layout)
        return widget
    
    def _create_symbolic_form(self) -> QWidget:
        """Create form for symbolic/motif relationships."""
        widget = QWidget()
        layout = QFormLayout()
        
        # Motif selection
        self.motif_combo = QComboBox()
        if self.available_motifs:
            for motif in self.available_motifs:
                self.motif_combo.addItem(motif.name, motif.id)
        else:
            self.motif_combo.addItem("(No motifs available - create one first)", None)
        layout.addRow("Symbolic Motif:", self.motif_combo)
        
        help_text = QLabel(
            "<i>Symbolic relationships connect characters to abstract concepts like "
            "'food', 'authority', 'violence', etc. via motifs.</i>"
        )
        help_text.setWordWrap(True)
        layout.addRow("", help_text)
        
        # Description
        self.motif_description_input = QTextEdit()
        self.motif_description_input.setAcceptRichText(False)
        self.motif_description_input.setMaximumHeight(80)
        self.motif_description_input.setPlaceholderText(
            "How does this character relate to this concept?"
        )
        layout.addRow("Description:", self.motif_description_input)
        
        # Attributes/sliders for abstract relationship
        attributes_label = QLabel("<b>Relationship Dynamics:</b>")
        layout.addRow(attributes_label)
        
        self.symbolic_sliders = {}
        for attr in ["obsession", "fear", "comfort", "control"]:
            slider_widget = self._create_slider_row(attr)
            layout.addRow(f"  {attr.capitalize()}:", slider_widget)
            self.symbolic_sliders[attr] = slider_widget
        
        # Add custom attribute button
        add_attr_btn = QPushButton("+ Add Custom Attribute")
        add_attr_btn.clicked.connect(self._add_custom_symbolic_attribute)
        layout.addRow("", add_attr_btn)
        
        # Primary motif flag
        help_text2 = QLabel(
            "<i>Custom attributes let you define additional relationship dimensions.</i>"
        )
        help_text2.setWordWrap(True)
        layout.addRow("", help_text2)
        
        widget.setLayout(layout)
        return widget
    
    def _create_slider_row(self, attr_name: str) -> QWidget:
        """Create a slider with value display."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(25)
        
        value_label = QLabel("0.5")
        value_label.setMinimumWidth(40)
        
        slider.valueChanged.connect(
            lambda v: value_label.setText(f"{v/100:.1f}")
        )
        
        layout.addWidget(slider)
        layout.addWidget(value_label)
        
        widget.setLayout(layout)
        widget.slider = slider  # Store reference for easy access
        widget.value_label = value_label
        return widget
    
    def _add_custom_symbolic_attribute(self) -> None:
        """Add a custom attribute slider to symbolic form."""
        # TODO: Implement dialog to add custom attributes
        pass
    
    def _load_relationship_data(self) -> None:
        """Load existing relationship data for editing."""
        if isinstance(self.edit_relationship, Relationship):
            # Interpersonal relationship
            self.interpersonal_radio.setChecked(True)
            self._on_type_changed(True)
            
            # Find and select the other character
            other_id = (self.edit_relationship.character_b_id 
                       if self.edit_relationship.character_a_id == self.character.id 
                       else self.edit_relationship.character_a_id)
            for i in range(self.character_combo.count()):
                if self.character_combo.itemData(i) == other_id:
                    self.character_combo.setCurrentIndex(i)
                    break
            
            # Set fields
            self.rel_type_input.setText(self.edit_relationship.relationship_type or "")
            self.description_input.setPlainText(self.edit_relationship.description or "")
            self.status_input.setText(self.edit_relationship.status or "")
            self.began_at_input.setText(self.edit_relationship.began_at or "")
            
            # Set sliders
            if self.edit_relationship.attributes:
                for attr_name, slider_widget in self.interpersonal_sliders.items():
                    if attr_name in self.edit_relationship.attributes:
                        value = int(self.edit_relationship.attributes[attr_name] * 100)
                        slider_widget.slider.setValue(value)
        
        elif isinstance(self.edit_relationship, CharacterMotifRelationship):
            # Symbolic relationship
            self.symbolic_radio.setChecked(True)
            self._on_type_changed(True)
            
            # Find and select the motif
            for i in range(self.motif_combo.count()):
                if self.motif_combo.itemData(i) == self.edit_relationship.motif_id:
                    self.motif_combo.setCurrentIndex(i)
                    break
            
            # Set fields
            self.motif_description_input.setPlainText(self.edit_relationship.description or "")
            
            # Set sliders
            if self.edit_relationship.attributes:
                for attr_name, slider_widget in self.symbolic_sliders.items():
                    if attr_name in self.edit_relationship.attributes:
                        value = int(self.edit_relationship.attributes[attr_name] * 100)
                        slider_widget.slider.setValue(value)
    
    def _on_type_changed(self, checked: bool) -> None:
        """Handle relationship type change."""
        if self.interpersonal_radio.isChecked():
            self.interpersonal_form.show()
            self.symbolic_form.hide()
        else:
            self.interpersonal_form.hide()
            self.symbolic_form.show()
        
        # Force the dialog to resize to fit the currently visible content
        self.adjustSize()
    
    def _on_accept(self) -> None:
        """Validate and prepare relationship data."""
        if self.interpersonal_radio.isChecked():
            # Validate interpersonal relationship
            if self.character_combo.count() == 0:
                # No other characters available
                return
            
            other_char_id = self.character_combo.currentData()
            rel_type = self.rel_type_input.text().strip()
            
            if not rel_type:
                # Could show error message
                return
            
            # Collect slider values
            attributes = {}
            for attr_name, slider_widget in self.interpersonal_sliders.items():
                attributes[attr_name] = slider_widget.slider.value() / 100.0
            
            self.relationship_data = {
                'type': 'interpersonal',
                'id': self.edit_relationship.id if self.is_editing else None,
                'character_a_id': self.character.id,
                'character_b_id': other_char_id,
                'relationship_type': rel_type,
                'description': self.description_input.toPlainText().strip() or None,
                'attributes': attributes,
                'status': self.status_input.text().strip() or None,
                'began_at': self.began_at_input.text().strip() or None,
            }
        else:
            # Validate symbolic relationship
            motif_id = self.motif_combo.currentData()
            if motif_id is None:
                # No motifs available
                return
            
            # Collect slider values
            attributes = {}
            for attr_name, slider_widget in self.symbolic_sliders.items():
                attributes[attr_name] = slider_widget.slider.value() / 100.0
            
            self.relationship_data = {
                'type': 'symbolic',
                'id': self.edit_relationship.id if self.is_editing else None,
                'character_id': self.character.id,
                'motif_id': motif_id,
                'description': self.motif_description_input.toPlainText().strip() or None,
                'attributes': attributes,
            }
        
        self.accept()
    
    def _get_character_display_name(self, character: Character) -> str:
        """Get display name for a character."""
        if character.nickname:
            return character.nickname
        if character.first_name:
            name_parts = [character.first_name]
            if character.last_name:
                name_parts.append(character.last_name)
            return " ".join(name_parts)
        return f"Character {character.id}"
    
    def get_relationship_data(self) -> Optional[dict]:
        """Get the created relationship data."""
        return self.relationship_data
