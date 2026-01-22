"""Event creation and editing dialog."""
from typing import Optional
from datetime import datetime

from PySide6.QtCore import Qt, QDateTime
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QDateTimeEdit,
    QSpinBox,
    QCheckBox,
    QPushButton,
    QWidget,
    QLabel,
    QScrollArea,
)

from nico.domain.models import Event
from nico.application.context import get_app_context


class EventDialog(QDialog):
    """Dialog for creating or editing an event."""
    
    def __init__(self, project_id: int, event: Optional[Event] = None, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.event = event
        self.is_editing = event is not None
        self.app_context = get_app_context()
        
        self.setWindowTitle("Edit Event" if self.is_editing else "New Event")
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)
        
        self._setup_ui()
        if self.is_editing:
            self._load_event_data()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        form_layout = QFormLayout()
        
        # Title (required)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Event name (required)")
        form_layout.addRow("Title:*", self.title_edit)
        
        # Event Type
        self.type_edit = QLineEdit()
        self.type_edit.setPlaceholderText("Battle, meeting, birth, discovery, etc.")
        form_layout.addRow("Type:", self.type_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("What happened during this event...")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_edit)
        
        # Timeline Section
        timeline_label = QLabel("<b>Timeline</b>")
        form_layout.addRow("", timeline_label)
        
        # Timeline Position (for relative ordering)
        self.position_spin = QSpinBox()
        self.position_spin.setMinimum(0)
        self.position_spin.setMaximum(999999)
        self.position_spin.setValue(0)
        self.position_spin.setToolTip("Relative position for ordering events")
        form_layout.addRow("Position:", self.position_spin)
        
        # Occurred At
        self.occurred_edit = QDateTimeEdit()
        self.occurred_edit.setCalendarPopup(True)
        self.occurred_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.occurred_edit.setSpecialValueText("Not set")
        form_layout.addRow("Occurred At:", self.occurred_edit)
        
        # Ended At
        self.ended_edit = QDateTimeEdit()
        self.ended_edit.setCalendarPopup(True)
        self.ended_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.ended_edit.setSpecialValueText("Not set")
        form_layout.addRow("Ended At:", self.ended_edit)
        
        # Duration
        self.duration_edit = QLineEdit()
        self.duration_edit.setPlaceholderText("e.g., 3 days, 2 hours, 6 months")
        form_layout.addRow("Duration:", self.duration_edit)
        
        # Event Details Section
        details_label = QLabel("<b>Event Details</b>")
        form_layout.addRow("", details_label)
        
        # Scope
        self.scope_edit = QLineEdit()
        self.scope_edit.setPlaceholderText("Personal, local, regional, global, etc.")
        form_layout.addRow("Scope:", self.scope_edit)
        
        # Significance
        self.significance_edit = QTextEdit()
        self.significance_edit.setPlaceholderText("Why this event matters...")
        self.significance_edit.setMaximumHeight(80)
        form_layout.addRow("Significance:", self.significance_edit)
        
        # Outcome
        self.outcome_edit = QTextEdit()
        self.outcome_edit.setPlaceholderText("Result or consequence of the event...")
        self.outcome_edit.setMaximumHeight(80)
        form_layout.addRow("Outcome:", self.outcome_edit)
        
        # Note about participants and locations
        info_label = QLabel(
            "Note: Participants (characters) and locations can be linked to this event "
            "via the advanced editor in future versions."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        form_layout.addRow("", info_label)
        
        # AI exclusion
        self.exclude_ai_checkbox = QCheckBox("Exclude from AI suggestions")
        form_layout.addRow("", self.exclude_ai_checkbox)
        
        content.setLayout(form_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_event)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _load_event_data(self) -> None:
        """Load existing event data into the form."""
        if not self.event:
            return
        
        self.title_edit.setText(self.event.title)
        self.type_edit.setText(self.event.event_type or "")
        self.description_edit.setPlainText(self.event.description or "")
        
        self.position_spin.setValue(self.event.timeline_position)
        
        if self.event.occurred_at:
            self.occurred_edit.setDateTime(QDateTime(
                self.event.occurred_at.year,
                self.event.occurred_at.month,
                self.event.occurred_at.day,
                self.event.occurred_at.hour,
                self.event.occurred_at.minute,
            ))
        
        if self.event.ended_at:
            self.ended_edit.setDateTime(QDateTime(
                self.event.ended_at.year,
                self.event.ended_at.month,
                self.event.ended_at.day,
                self.event.ended_at.hour,
                self.event.ended_at.minute,
            ))
        
        self.duration_edit.setText(self.event.duration or "")
        self.scope_edit.setText(self.event.scope or "")
        self.significance_edit.setPlainText(self.event.significance or "")
        self.outcome_edit.setPlainText(self.event.outcome or "")
        self.exclude_ai_checkbox.setChecked(self.event.exclude_from_ai)
    
    def _save_event(self) -> None:
        """Save the event to database."""
        # Validate required fields
        title = self.title_edit.text().strip()
        if not title:
            # TODO: Show error dialog
            print("Event title is required")
            return
        
        # Collect data
        data = {
            "title": title,
            "event_type": self.type_edit.text() or None,
            "description": self.description_edit.toPlainText() or None,
            "timeline_position": self.position_spin.value(),
            "duration": self.duration_edit.text() or None,
            "scope": self.scope_edit.text() or None,
            "significance": self.significance_edit.toPlainText() or None,
            "outcome": self.outcome_edit.toPlainText() or None,
            "exclude_from_ai": self.exclude_ai_checkbox.isChecked(),
        }
        
        # Handle datetime fields
        occurred_dt = self.occurred_edit.dateTime()
        if occurred_dt and occurred_dt.isValid() and occurred_dt.toString() != "":
            data["occurred_at"] = datetime(
                occurred_dt.date().year(),
                occurred_dt.date().month(),
                occurred_dt.date().day(),
                occurred_dt.time().hour(),
                occurred_dt.time().minute(),
            )
        
        ended_dt = self.ended_edit.dateTime()
        if ended_dt and ended_dt.isValid() and ended_dt.toString() != "":
            data["ended_at"] = datetime(
                ended_dt.date().year(),
                ended_dt.date().month(),
                ended_dt.date().day(),
                ended_dt.time().hour(),
                ended_dt.time().minute(),
            )
        
        try:
            if self.is_editing:
                # Update existing event
                self.app_context.event_service.update_event(
                    self.event.id,
                    **data
                )
            else:
                # Create new event
                self.app_context.event_service.create_event(
                    self.project_id,
                    **data
                )
            
            self.app_context.commit()
            self.accept()
        except Exception as e:
            self.app_context.rollback()
            # TODO: Show error dialog
            print(f"Error saving event: {e}")
