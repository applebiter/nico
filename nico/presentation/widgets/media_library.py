"""Media library widget for browsing and managing project media."""
from pathlib import Path
from typing import Optional
import hashlib
import shutil

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QMessageBox,
    QScrollArea,
    QSplitter,
)

from nico.domain.models import Media
from nico.application.context import AppContext
from nico.presentation.widgets.media_upload_dialog import MediaUploadDialog
from nico.presentation.widgets.image_generation_dialog import ImageGenerationDialog
from PIL import Image


class MediaLibraryWidget(QWidget):
    """Widget for browsing and managing project media library."""
    
    media_selected = Signal(int)  # media_id
    media_attached = Signal(int, str, int)  # media_id, entity_type, entity_id
    
    def __init__(self, app_context: AppContext) -> None:
        super().__init__()
        self.app_context = app_context
        self.current_project_id: Optional[int] = None
        self.current_media: Optional[Media] = None
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title_label = QLabel("📚 Media Library")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.upload_btn = QPushButton("⬆️ Upload")
        self.upload_btn.clicked.connect(self._on_upload_media)
        toolbar.addWidget(self.upload_btn)
        
        self.generate_btn = QPushButton("✨ Generate")
        self.generate_btn.clicked.connect(self._on_generate_media)
        toolbar.addWidget(self.generate_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self._on_delete_media)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_media_list)
        toolbar.addWidget(self.refresh_btn)
        
        layout.addLayout(toolbar)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Images", "Audio", "Video"])
        self.type_filter.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search media...")
        self.search_input.textChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.search_input)
        
        layout.addLayout(filter_layout)
        
        # Main content - splitter with list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Media list
        self.media_list = QListWidget()
        self.media_list.currentItemChanged.connect(self._on_media_selected)
        splitter.addWidget(self.media_list)
        
        # Media details panel
        details_widget = QWidget()
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Select media to preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background: #f5f5f5;")
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        details_layout.addWidget(preview_group)
        
        # Metadata area
        metadata_group = QGroupBox("Metadata")
        metadata_layout = QVBoxLayout()
        
        # Filename
        self.filename_label = QLabel("-")
        metadata_layout.addWidget(QLabel("<b>Filename:</b>"))
        metadata_layout.addWidget(self.filename_label)
        
        # Title (editable)
        metadata_layout.addWidget(QLabel("<b>Title:</b>"))
        self.title_input = QLineEdit()
        self.title_input.textChanged.connect(self._on_metadata_changed)
        metadata_layout.addWidget(self.title_input)
        
        # Description (editable)
        metadata_layout.addWidget(QLabel("<b>Description:</b>"))
        self.description_input = QTextEdit()
        self.description_input.setAcceptRichText(False)
        self.description_input.setMaximumHeight(80)
        self.description_input.textChanged.connect(self._on_metadata_changed)
        metadata_layout.addWidget(self.description_input)
        
        # Info
        self.info_label = QLabel("-")
        self.info_label.setWordWrap(True)
        metadata_layout.addWidget(QLabel("<b>Info:</b>"))
        metadata_layout.addWidget(self.info_label)
        
        metadata_layout.addStretch()
        metadata_group.setLayout(metadata_layout)
        details_layout.addWidget(metadata_group)
        
        details_widget.setLayout(details_layout)
        splitter.addWidget(details_widget)
        
        splitter.setSizes([300, 400])
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        
    def load_project(self, project_id: int) -> None:
        """Load media for a project."""
        self.current_project_id = project_id
        self.refresh_media_list()
        
    def refresh_media_list(self) -> None:
        """Refresh the media list from database."""
        if not self.current_project_id:
            return
        
        self.media_list.clear()
        self.current_media = None
        self._clear_details()
        
        try:
            media_items = self.app_context.media_service.list_media(self.current_project_id)
            
            for media in media_items:
                item = QListWidgetItem()
                
                # Icon based on media type
                icon_map = {
                    "image": "🖼️",
                    "audio": "🎵",
                    "video": "🎬",
                }
                icon = icon_map.get(media.media_type, "📄")
                
                # Display text
                display_name = media.get_display_title()
                item.setText(f"{icon} {display_name}")
                item.setData(Qt.ItemDataRole.UserRole, media.id)
                
                self.media_list.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load media: {str(e)}")
    
    def _on_media_selected(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]) -> None:
        """Handle media selection."""
        if not current:
            self._clear_details()
            return
        
        media_id = current.data(Qt.ItemDataRole.UserRole)
        if not media_id:
            return
        
        try:
            self.current_media = self.app_context.media_service.get_media(media_id)
            if self.current_media:
                self._display_media_details(self.current_media)
                self.media_selected.emit(media_id)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load media details: {str(e)}")
    
    def _display_media_details(self, media: Media) -> None:
        """Display media details in the panel."""
        # Update filename
        self.filename_label.setText(media.original_filename)
        
        # Update title
        self.title_input.blockSignals(True)
        self.title_input.setText(media.title or "")
        self.title_input.blockSignals(False)
        
        # Update description
        self.description_input.blockSignals(True)
        self.description_input.setPlainText(media.description or "")
        self.description_input.blockSignals(False)
        
        # Update info
        info_parts = [
            f"Type: {media.media_type}",
            f"Size: {self._format_file_size(media.file_size)}",
        ]
        
        if media.width and media.height:
            info_parts.append(f"Dimensions: {media.width}×{media.height}")
        
        if media.duration:
            info_parts.append(f"Duration: {self._format_duration(media.duration)}")
        
        self.info_label.setText("\n".join(info_parts))
        
        # Update preview
        if media.media_type == "image":
            self._display_image_preview(media)
        elif media.media_type == "audio":
            self.preview_label.setText(f"🎵 Audio file\n\n{media.original_filename}")
        elif media.media_type == "video":
            self.preview_label.setText(f"🎬 Video file\n\n{media.original_filename}")
    
    def _display_image_preview(self, media: Media) -> None:
        """Display image preview."""
        file_path = Path.cwd() / media.file_path
        
        if file_path.exists():
            pixmap = QPixmap(str(file_path))
            if not pixmap.isNull():
                # Scale to fit preview area
                scaled = pixmap.scaled(
                    400, 400,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)
            else:
                self.preview_label.setText("Failed to load image")
        else:
            self.preview_label.setText("Image file not found")
    
    def _clear_details(self) -> None:
        """Clear the details panel."""
        self.filename_label.setText("-")
        self.title_input.clear()
        self.description_input.clear()
        self.info_label.setText("-")
        self.preview_label.clear()
        self.preview_label.setText("Select media to preview")
    
    def _on_metadata_changed(self) -> None:
        """Handle metadata changes."""
        if not self.current_media:
            return
        
        # Save changes to database
        try:
            self.app_context.media_service.update_media(
                self.current_media.id,
                title=self.title_input.text().strip() or None,
                description=self.description_input.toPlainText().strip() or None,
            )
        except Exception as e:
            print(f"Failed to update media metadata: {e}")
    
    def _on_filter_changed(self) -> None:
        """Handle filter changes."""
        # TODO: Implement filtering
        pass
    
    def _on_upload_media(self) -> None:
        """Handle upload button click."""
        if not self.current_project_id:
            QMessageBox.warning(self, "No Project", "Please select a project first.")
            return
        
        dialog = MediaUploadDialog(self.current_project_id, self.app_context, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_media_list()
    
    def _on_generate_media(self) -> None:
        """Handle generate button click."""
        if not self.current_project_id:
            QMessageBox.warning(self, "No Project", "Please select a project first.")
            return
        
        # Open image generation dialog
        dialog = ImageGenerationDialog(
            app_context=self.app_context,
            entity_type=None,  # Standalone generation, not tied to entity
            entity_id=None,
            parent=self
        )
        
        if dialog.exec() == dialog.DialogCode.Accepted:
            image_path, prompt = dialog.get_result()
            
            if image_path and image_path.exists():
                try:
                    # Import the generated image into media library
                    self._import_generated_image(image_path, prompt)
                    self.refresh_media_list()
                    
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Generated image added to media library:\n{image_path.name}"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Import Error",
                        f"Failed to import generated image:\n{str(e)}"
                    )
    
    def _import_generated_image(self, source_path: Path, prompt: str) -> None:
        """Import a generated image into the media library."""
        # Calculate file hash
        hasher = hashlib.sha256()
        with open(source_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()
        
        # Check for duplicates
        existing = self.app_context._session.query(Media).filter(
            Media.project_id == self.current_project_id,
            Media.file_hash == file_hash
        ).first()
        
        if existing:
            # File already exists, just return
            return
        
        # Get image dimensions
        width, height = None, None
        try:
            with Image.open(source_path) as img:
                width, height = img.size
        except Exception as e:
            print(f"Could not read image dimensions: {e}")
        
        # Determine destination path
        media_dir = Path("media") / str(self.current_project_id)
        media_dir.mkdir(parents=True, exist_ok=True)
        
        # Create safe filename
        original_name = source_path.name
        dest_path = media_dir / original_name
        
        # Handle name conflicts
        counter = 1
        while dest_path.exists():
            stem = source_path.stem
            suffix = source_path.suffix
            dest_path = media_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        # Copy file
        shutil.copy2(source_path, dest_path)
        
        # Create media record
        media = self.app_context.media_service.create_media(
            project_id=self.current_project_id,
            media_type='image',
            original_filename=original_name,
            file_path=str(dest_path),
            mime_type='image/png',
            file_size=dest_path.stat().st_size,
            file_hash=file_hash,
            width=width,
            height=height,
            title=None,
            description=f"Generated: {prompt[:200]}" if prompt else None,
        )
    
    def _on_delete_media(self) -> None:
        """Handle delete button click."""
        if not self.current_media:
            QMessageBox.information(self, "No Selection", "Please select media to delete.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{self.current_media.get_display_title()}'?\n\n"
            "This will remove the media from the library and all attachments.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete file from disk
                file_path = Path.cwd() / self.current_media.file_path
                if file_path.exists():
                    file_path.unlink()
                
                # Delete from database
                self.app_context.media_service.delete_media(self.current_media.id)
                
                # Refresh list
                self.refresh_media_list()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete media: {str(e)}")
    
    def _format_file_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
