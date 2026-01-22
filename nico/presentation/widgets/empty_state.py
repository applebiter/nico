"""Empty state widget for when no projects exist."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)


class EmptyStateWidget(QWidget):
    """Widget displayed when no projects exist."""
    
    create_project_requested = Signal()
    
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon/emoji
        icon_label = QLabel("📚")
        icon_label.setStyleSheet("font-size: 72px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title = QLabel("Welcome to Nico")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Narrative Insight Composition Output")
        subtitle.setStyleSheet("font-size: 16px; color: #666; margin-bottom: 30px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Message
        message = QLabel(
            "You don't have any projects yet.\n"
            "Create your first project to start writing."
        )
        message.setStyleSheet("font-size: 14px; color: #888; margin-bottom: 30px;")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Create project button
        create_btn = QPushButton("➕ Create Your First Project")
        create_btn.setStyleSheet(
            "font-size: 16px; padding: 12px 24px; "
            "background-color: #4CAF50; color: white; "
            "border: none; border-radius: 4px;"
        )
        create_btn.clicked.connect(self.create_project_requested.emit)
        create_btn.setMaximumWidth(300)
        layout.addWidget(create_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        
        self.setLayout(layout)
