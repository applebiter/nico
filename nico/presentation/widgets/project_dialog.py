"""Project creation and editing dialog."""
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
)

from nico.domain.models import Project
from nico.application.context import get_app_context


class ProjectDialog(QDialog):
    """Dialog for creating or editing a project."""
    
    def __init__(self, project: Optional[Project] = None, parent=None):
        super().__init__(parent)
        self.project = project
        self.is_editing = project is not None
        self.app_context = get_app_context()
        
        self.setWindowTitle("Edit Project" if self.is_editing else "New Project")
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        
        self._setup_ui()
        if self.is_editing:
            self._load_project_data()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Form layout for fields
        form = QFormLayout()
        
        # Title (required)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter project title...")
        form.addRow("Title:*", self.title_edit)
        
        # Author (optional)
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Author name")
        form.addRow("Author:", self.author_edit)
        
        # Description (optional)
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Project description or overview...")
        self.description_edit.setMaximumHeight(150)
        form.addRow("Description:", self.description_edit)
        
        layout.addLayout(form)
        
        # Required field note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        layout.addWidget(note_label)
        
        layout.addStretch()
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_project)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _load_project_data(self) -> None:
        """Load existing project data into the form."""
        if not self.project:
            return
        
        self.title_edit.setText(self.project.title or "")
        self.author_edit.setText(self.project.author or "")
        self.description_edit.setPlainText(self.project.description or "")
    
    def _save_project(self) -> None:
        """Save the project to database."""
        # Validate required fields
        title = self.title_edit.text().strip()
        if not title:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Missing Title",
                "Please enter a title for the project."
            )
            self.title_edit.setFocus()
            return
        
        # Collect data
        data = {
            "title": title,
            "author": self.author_edit.text().strip() or None,
            "description": self.description_edit.toPlainText().strip() or None,
        }
        
        try:
            if self.is_editing:
                # Update existing project
                for key, value in data.items():
                    setattr(self.project, key, value)
                self.app_context.commit()
            else:
                # Create new project
                project = Project(**data)
                self.app_context._session.add(project)
                self.app_context.commit()
            
            self.accept()
            
        except Exception as e:
            self.app_context.rollback()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while saving the project:\n{str(e)}"
            )
