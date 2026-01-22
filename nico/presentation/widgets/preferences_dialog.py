"""Preferences dialog widget."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSlider,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QDialogButtonBox,
)

from nico.preferences import get_preferences, ThemeMode


class PreferencesDialog(QDialog):
    """Dialog for user preferences."""
    
    # Signal emitted when preferences are saved
    preferences_changed = Signal()
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.prefs = get_preferences()
        self._setup_ui()
        self._load_current_values()
        
    def _setup_ui(self) -> None:
        """Set up the dialog layout."""
        layout = QVBoxLayout()
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()
        
        # Theme selector
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("🌙 Dark Mode", "dark")
        self.theme_combo.addItem("☀️ Light Mode", "light")
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        # Font scale
        font_scale_layout = QHBoxLayout()
        self.font_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_scale_slider.setMinimum(75)
        self.font_scale_slider.setMaximum(150)
        self.font_scale_slider.setSingleStep(5)
        self.font_scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.font_scale_slider.setTickInterval(25)
        self.font_scale_slider.valueChanged.connect(self._update_font_scale_label)
        font_scale_layout.addWidget(self.font_scale_slider)
        
        self.font_scale_label = QLabel("100%")
        self.font_scale_label.setMinimumWidth(50)
        font_scale_layout.addWidget(self.font_scale_label)
        
        appearance_layout.addRow("Font Scale:", font_scale_layout)
        
        # Editor font
        self.editor_font_combo = QComboBox()
        self.editor_font_combo.addItems([
            "Georgia",
            "Times New Roman",
            "Arial",
            "Helvetica",
            "Courier New",
            "Liberation Serif",
            "Liberation Sans",
            "Liberation Mono",
        ])
        appearance_layout.addRow("Editor Font:", self.editor_font_combo)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Info text
        info_label = QLabel(
            "Note: Some changes may require restarting the application."
        )
        info_label.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_preferences)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def _load_current_values(self) -> None:
        """Load current preference values into UI."""
        # Theme
        index = self.theme_combo.findData(self.prefs.theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Font scale
        self.font_scale_slider.setValue(self.prefs.font_scale)
        self._update_font_scale_label(self.prefs.font_scale)
        
        # Editor font
        index = self.editor_font_combo.findText(self.prefs.editor_font)
        if index >= 0:
            self.editor_font_combo.setCurrentIndex(index)
    
    def _update_font_scale_label(self, value: int) -> None:
        """Update font scale label."""
        self.font_scale_label.setText(f"{value}%")
    
    def _save_preferences(self) -> None:
        """Save preferences and close dialog."""
        # Get values from UI
        self.prefs.theme = self.theme_combo.currentData()
        self.prefs.font_scale = self.font_scale_slider.value()
        self.prefs.editor_font = self.editor_font_combo.currentText()
        
        # Save to disk
        self.prefs.save()
        
        # Emit signal
        self.preferences_changed.emit()
        
        self.accept()
