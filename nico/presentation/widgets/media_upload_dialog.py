"""Media upload dialog for adding files to the media library."""
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional
from PIL import Image

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nico.application.context import AppContext


class MediaUploadDialog(QDialog):
    """Dialog for uploading media files to the library."""
    
    def __init__(self, project_id: int, app_context: AppContext, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.project_id = project_id
        self.app_context = app_context
        self.selected_file: Optional[Path] = None
        self.media_id: Optional[int] = None
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.setWindowTitle("Upload Media")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("File:"))
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        file_layout.addWidget(self.file_label, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._on_browse)
        file_layout.addWidget(browse_btn)
        
        layout.addLayout(file_layout)
        
        # Metadata form
        form_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Optional: override filename")
        form_layout.addRow("Title:", self.title_input)
        
        self.description_input = QTextEdit()
        self.description_input.setAcceptRichText(False)
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Optional description...")
        form_layout.addRow("Description:", self.description_input)
        
        self.attribution_input = QLineEdit()
        self.attribution_input.setPlaceholderText("e.g., 'Photo by John Doe'")
        form_layout.addRow("Attribution:", self.attribution_input)
        
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("e.g., 'https://example.com/image.jpg'")
        form_layout.addRow("Source URL:", self.source_input)
        
        layout.addLayout(form_layout)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(self.info_label)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def _on_browse(self) -> None:
        """Handle browse button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Media File",
            "",
            "Media Files (*.jpg *.jpeg *.png *.gif *.webp *.mp3 *.wav *.ogg *.mp4 *.mkv *.avi);;All Files (*)"
        )
        
        if file_path:
            self.selected_file = Path(file_path)
            self.file_label.setText(self.selected_file.name)
            self._update_info()
    
    def _update_info(self) -> None:
        """Update file info display."""
        if not self.selected_file or not self.selected_file.exists():
            self.info_label.setText("")
            return
        
        info_parts = []
        
        # File size
        size = self.selected_file.stat().st_size
        info_parts.append(f"Size: {self._format_file_size(size)}")
        
        # MIME type
        mime_type, _ = mimetypes.guess_type(str(self.selected_file))
        if mime_type:
            info_parts.append(f"Type: {mime_type}")
            
            # Get dimensions for images
            if mime_type.startswith("image/"):
                try:
                    with Image.open(self.selected_file) as img:
                        info_parts.append(f"Dimensions: {img.width}×{img.height}")
                except Exception:
                    pass
        
        self.info_label.setText("\n".join(info_parts))
    
    def _on_accept(self) -> None:
        """Handle OK button click."""
        if not self.selected_file or not self.selected_file.exists():
            QMessageBox.warning(self, "No File", "Please select a file to upload.")
            return
        
        try:
            # Determine media type
            mime_type, _ = mimetypes.guess_type(str(self.selected_file))
            if not mime_type:
                mime_type = "application/octet-stream"
            
            if mime_type.startswith("image/"):
                media_type = "image"
            elif mime_type.startswith("audio/"):
                media_type = "audio"
            elif mime_type.startswith("video/"):
                media_type = "video"
            else:
                QMessageBox.warning(
                    self,
                    "Unsupported Type",
                    "This file type is not supported. Please select an image, audio, or video file."
                )
                return
            
            # Calculate file hash
            file_hash = self._calculate_hash(self.selected_file)
            
            # Check for duplicates
            existing_media = self.app_context._session.query(
                self.app_context._session.query(type('Media', (), {})).model_class
            ).filter_by(
                project_id=self.project_id,
                file_hash=file_hash
            ).first() if hasattr(self.app_context, '_session') else None
            
            # Create media directory structure
            media_dir = Path.cwd() / "media" / str(self.project_id)
            media_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy file to media directory with unique name
            file_extension = self.selected_file.suffix
            safe_name = self._make_safe_filename(self.selected_file.stem)
            dest_file = media_dir / f"{safe_name}{file_extension}"
            
            # Handle name conflicts
            counter = 1
            while dest_file.exists():
                dest_file = media_dir / f"{safe_name}_{counter}{file_extension}"
                counter += 1
            
            # Copy file
            import shutil
            shutil.copy2(self.selected_file, dest_file)
            
            # Get file info
            file_size = dest_file.stat().st_size
            width = height = None
            duration = None
            
            if media_type == "image":
                try:
                    with Image.open(dest_file) as img:
                        width, height = img.width, img.height
                except Exception:
                    pass
            
            # Create relative path from project root
            relative_path = dest_file.relative_to(Path.cwd())
            
            # Create media record
            media = self.app_context.media_service.create_media(
                project_id=self.project_id,
                media_type=media_type,
                original_filename=self.selected_file.name,
                file_path=str(relative_path),
                mime_type=mime_type,
                file_size=file_size,
                file_hash=file_hash,
                width=width,
                height=height,
                duration=duration,
                title=self.title_input.text().strip() or None,
                description=self.description_input.toPlainText().strip() or None,
                attribution=self.attribution_input.text().strip() or None,
                source_url=self.source_input.text().strip() or None,
            )
            
            self.media_id = media.id
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Upload Failed",
                f"Failed to upload media:\n\n{str(e)}"
            )
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _make_safe_filename(self, name: str) -> str:
        """Make a safe filename by removing/replacing problematic characters."""
        import re
        # Replace spaces and special chars with underscores
        safe = re.sub(r'[^\w\-]', '_', name)
        # Remove multiple consecutive underscores
        safe = re.sub(r'_+', '_', safe)
        # Remove leading/trailing underscores
        safe = safe.strip('_')
        return safe or "media"
    
    def _format_file_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_media_id(self) -> Optional[int]:
        """Get the ID of the uploaded media."""
        return self.media_id
