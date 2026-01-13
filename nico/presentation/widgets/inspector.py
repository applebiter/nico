"""Inspector widget - properties and metadata panel."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QScrollArea,
)


class InspectorWidget(QWidget):
    """Right panel: Properties and metadata for selected item."""
    
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("🔍 Inspector")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scene metadata group
        metadata_group = QGroupBox("Scene Metadata")
        metadata_layout = QFormLayout()
        
        title_field = QLineEdit("Morning in the Tower")
        metadata_layout.addRow("Title:", title_field)
        
        beat_field = QLineEdit("Opening image")
        metadata_layout.addRow("Beat:", beat_field)
        
        pov_field = QLineEdit("Elara")
        metadata_layout.addRow("POV:", pov_field)
        
        setting_field = QLineEdit("Mage Tower")
        metadata_layout.addRow("Setting:", setting_field)
        
        metadata_group.setLayout(metadata_layout)
        content_layout.addWidget(metadata_group)
        
        # Scene summary group
        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout()
        
        summary_text = QTextEdit()
        summary_text.setPlaceholderText("Brief summary of this scene...")
        summary_text.setMaximumHeight(100)
        summary_text.setPlainText("Elara wakes early on the morning of her examination, "
                                  "reflecting on her five years of training.")
        
        summary_layout.addWidget(summary_text)
        summary_group.setLayout(summary_layout)
        content_layout.addWidget(summary_group)
        
        # Notes group
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        
        notes_text = QTextEdit()
        notes_text.setPlaceholderText("Research notes, ideas, reminders...")
        notes_text.setMaximumHeight(150)
        notes_text.setPlainText("- Establish Elara's daily routine\n"
                                "- Show her relationship with Theron\n"
                                "- Foreshadow the examination")
        
        notes_layout.addWidget(notes_text)
        notes_group.setLayout(notes_layout)
        content_layout.addWidget(notes_group)
        
        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout()
        
        stats_layout.addRow("Word Count:", QLabel("1,250"))
        stats_layout.addRow("Target:", QLabel("1,000-1,500"))
        stats_layout.addRow("Created:", QLabel("Jan 13, 2026"))
        stats_layout.addRow("Modified:", QLabel("Jan 13, 2026"))
        
        stats_group.setLayout(stats_layout)
        content_layout.addWidget(stats_group)
        
        # AI Settings group
        ai_group = QGroupBox("AI Settings")
        ai_layout = QFormLayout()
        
        ai_layout.addRow("Exclude from AI:", QLabel("No"))
        
        ai_group.setLayout(ai_layout)
        content_layout.addWidget(ai_group)
        
        content_layout.addStretch()
        
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
