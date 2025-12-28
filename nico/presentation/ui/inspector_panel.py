"""Inspector panel for displaying and editing item metadata."""

import json
from typing import Optional
from uuid import UUID

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class InspectorPanel(QWidget):
    """Panel for viewing and editing metadata of selected items."""

    # Signals for metadata changes
    title_changed = Signal(str, UUID, str)  # (item_type, item_id, new_title)
    synopsis_changed = Signal(str, UUID, str)  # (item_type, item_id, new_synopsis)
    
    def __init__(self, parent: Optional[object] = None):
        super().__init__(parent)
        self.current_item_type: Optional[str] = None
        self.current_item_id: Optional[UUID] = None
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the inspector UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Inspector")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(15)
        
        # Form layout for fields
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # Type field
        self.type_label = QLabel("-")
        self.form_layout.addRow("Type:", self.type_label)
        
        # Title field
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter title...")
        self.title_edit.editingFinished.connect(self._on_title_changed)
        self.form_layout.addRow("Title:", self.title_edit)
        
        # Synopsis field
        self.synopsis_edit = QTextEdit()
        self.synopsis_edit.setPlaceholderText("Enter synopsis...")
        self.synopsis_edit.setMaximumHeight(100)
        self.synopsis_edit.textChanged.connect(self._on_synopsis_changed)
        self.form_layout.addRow("Synopsis:", self.synopsis_edit)
        
        # Word count field (for scenes)
        self.word_count_label = QLabel("-")
        self.word_count_row = self.form_layout.rowCount()
        self.form_layout.addRow("Word Count:", self.word_count_label)
        
        # Status field (for scenes)
        self.status_label = QLabel("-")
        self.status_row = self.form_layout.rowCount()
        self.form_layout.addRow("Status:", self.status_label)
        
        self.content_layout.addLayout(self.form_layout)
        self.content_layout.addStretch()
        
        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll)
        
        # Initially hide editable fields
        self._show_empty_state()

    def _show_empty_state(self) -> None:
        """Show empty state when nothing is selected."""
        self.type_label.setText("-")
        self.title_edit.setText("")
        self.title_edit.setEnabled(False)
        self.synopsis_edit.setText("")
        self.synopsis_edit.setEnabled(False)
        self._hide_field(self.word_count_row)
        self._hide_field(self.status_row)

    def _hide_field(self, row: int) -> None:
        """Hide a form field row."""
        label = self.form_layout.itemAt(row, QFormLayout.ItemRole.LabelRole)
        field = self.form_layout.itemAt(row, QFormLayout.ItemRole.FieldRole)
        if label and label.widget():
            label.widget().hide()
        if field and field.widget():
            field.widget().hide()

    def _show_field(self, row: int) -> None:
        """Show a form field row."""
        label = self.form_layout.itemAt(row, QFormLayout.ItemRole.LabelRole)
        field = self.form_layout.itemAt(row, QFormLayout.ItemRole.FieldRole)
        if label and label.widget():
            label.widget().show()
        if field and field.widget():
            field.widget().show()

    def load_item(
        self,
        item_type: str,
        item_id: UUID,
        title: str,
        synopsis: Optional[str] = None,
        word_count: Optional[int] = None,
        status: Optional[str] = None,
    ) -> None:
        """Load item metadata into the inspector."""
        self.current_item_type = item_type
        self.current_item_id = item_id
        
        # Update type
        type_display = item_type.capitalize()
        self.type_label.setText(type_display)
        
        # Update title
        self.title_edit.blockSignals(True)
        self.title_edit.setText(title)
        self.title_edit.setEnabled(True)
        self.title_edit.blockSignals(False)
        
        # Update synopsis
        self.synopsis_edit.blockSignals(True)
        self.synopsis_edit.setText(synopsis or "")
        self.synopsis_edit.setEnabled(True)
        self.synopsis_edit.blockSignals(False)
        
        # Show/hide fields based on type
        if item_type == "scene":
            self._show_field(self.word_count_row)
            self._show_field(self.status_row)
            self.word_count_label.setText(str(word_count) if word_count else "0")
            self.status_label.setText(status or "draft")
        else:
            self._hide_field(self.word_count_row)
            self._hide_field(self.status_row)

    def update_word_count(self, count: int) -> None:
        """Update the word count display."""
        self.word_count_label.setText(str(count))

    def clear(self) -> None:
        """Clear the inspector."""
        self.current_item_type = None
        self.current_item_id = None
        self._show_empty_state()

    def _on_title_changed(self) -> None:
        """Handle title changes."""
        if self.current_item_id is None:
            return
        
        new_title = self.title_edit.text().strip()
        if new_title:
            self.title_changed.emit(self.current_item_type, self.current_item_id, new_title)

    def _on_synopsis_changed(self) -> None:
        """Handle synopsis changes."""
        if self.current_item_id is None:
            return
        
        new_synopsis = self.synopsis_edit.toPlainText().strip()
        self.synopsis_changed.emit(self.current_item_type, self.current_item_id, new_synopsis)
