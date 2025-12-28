"""Dialog for creating a new project."""

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class NewProjectDialog(QDialog):
    """Dialog for creating a new project."""

    def __init__(self, parent: Optional[object] = None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setMinimumWidth(500)
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)

        # Form layout for project details
        form = QFormLayout()

        # Project name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("My Novel")
        form.addRow("Project Name:", self.name_edit)

        # Author
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Your Name")
        form.addRow("Author:", self.author_edit)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Optional project description...")
        self.description_edit.setMaximumHeight(80)
        form.addRow("Description:", self.description_edit)

        # Project location
        location_layout = QHBoxLayout()
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("Choose project folder...")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_location)
        location_layout.addWidget(self.location_edit)
        location_layout.addWidget(self.browse_button)
        form.addRow("Location:", location_layout)

        # Local-only AI
        self.local_only_checkbox = QCheckBox("Restrict AI to local-only (recommended)")
        self.local_only_checkbox.setChecked(True)
        form.addRow("Privacy:", self.local_only_checkbox)

        layout.addLayout(form)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _browse_location(self) -> None:
        """Open folder browser for project location."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Project Location",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly,
        )
        if folder:
            self.location_edit.setText(folder)

    def get_project_data(self) -> dict:
        """Get the entered project data."""
        return {
            "name": self.name_edit.text().strip(),
            "author": self.author_edit.text().strip() or None,
            "description": self.description_edit.toPlainText().strip() or None,
            "path": Path(self.location_edit.text().strip()) if self.location_edit.text().strip() else None,
            "local_only_ai": self.local_only_checkbox.isChecked(),
        }

    def validate(self) -> tuple[bool, str]:
        """
        Validate the input data.
        
        Returns:
            (is_valid, error_message)
        """
        data = self.get_project_data()
        
        if not data["name"]:
            return False, "Project name is required"
        
        if not data["path"]:
            return False, "Project location is required"
        
        # Create full project path: location/project_name
        project_path = data["path"] / data["name"]
        if project_path.exists():
            return False, f"Folder already exists: {project_path}"
        
        return True, ""

    def accept(self) -> None:
        """Accept the dialog after validation."""
        is_valid, error = self.validate()
        if not is_valid:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", error)
            return
        
        super().accept()
