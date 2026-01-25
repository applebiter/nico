"""Media picker dialog for attaching media to entities."""
from pathlib import Path
from typing import Optional
import hashlib
import shutil

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nico.domain.models import Media
from nico.application.context import AppContext
from nico.presentation.widgets.media_upload_dialog import MediaUploadDialog
from nico.presentation.widgets.image_generation_dialog import ImageGenerationDialog
from PIL import Image


class MediaPickerDialog(QDialog):
    """Dialog for picking media to attach to an entity."""
    
    def __init__(
        self,
        project_id: int,
        app_context: AppContext,
        entity_type: str,
        entity_id: int,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.project_id = project_id
        self.app_context = app_context
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.selected_media: Optional[Media] = None
        self._setup_ui()
        self._load_media()
        
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.setWindowTitle("Attach Media")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        
        # Title
        layout.addWidget(QLabel("<h3>Select Media to Attach</h3>"))
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        upload_btn = QPushButton("⬆️ Upload New")
        upload_btn.clicked.connect(self._on_upload_new)
        toolbar.addWidget(upload_btn)
        
        generate_btn = QPushButton("✨ Generate")
        generate_btn.clicked.connect(self._on_generate_new)
        toolbar.addWidget(generate_btn)
        
        toolbar.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search media...")
        self.search_input.textChanged.connect(self._filter_media)
        toolbar.addWidget(self.search_input)
        
        layout.addLayout(toolbar)
        
        # Main content - splitter with list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Media list
        self.media_list = QListWidget()
        self.media_list.currentItemChanged.connect(self._on_media_selected)
        self.media_list.itemDoubleClicked.connect(self._on_media_double_clicked)
        splitter.addWidget(self.media_list)
        
        # Preview panel
        preview_widget = QWidget()
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        self.preview_label = QLabel("Select media to preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background: #f5f5f5;")
        preview_layout.addWidget(self.preview_label)
        
        # Caption input
        preview_layout.addWidget(QLabel("<b>Caption (optional):</b>"))
        self.caption_input = QTextEdit()
        self.caption_input.setAcceptRichText(False)
        self.caption_input.setMaximumHeight(60)
        self.caption_input.setPlaceholderText("Add a caption for this attachment...")
        preview_layout.addWidget(self.caption_input)
        
        # Info
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        preview_layout.addWidget(self.info_label)
        
        preview_widget.setLayout(preview_layout)
        splitter.addWidget(preview_widget)
        
        splitter.setSizes([300, 400])
        layout.addWidget(splitter)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def _load_media(self) -> None:
        """Load media from the library."""
        self.media_list.clear()
        
        try:
            media_items = self.app_context.media_service.list_media(self.project_id)
            
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
    
    def _filter_media(self) -> None:
        """Filter media list based on search term."""
        search_term = self.search_input.text().lower()
        
        for i in range(self.media_list.count()):
            item = self.media_list.item(i)
            text = item.text().lower()
            item.setHidden(search_term not in text)
    
    def _on_media_selected(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]) -> None:
        """Handle media selection."""
        if not current:
            self.selected_media = None
            self.preview_label.clear()
            self.preview_label.setText("Select media to preview")
            self.info_label.setText("")
            return
        
        media_id = current.data(Qt.ItemDataRole.UserRole)
        if not media_id:
            return
        
        try:
            self.selected_media = self.app_context.media_service.get_media(media_id)
            if self.selected_media:
                self._display_preview(self.selected_media)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load media: {str(e)}")
    
    def _on_media_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on media item."""
        self._on_accept()
    
    def _display_preview(self, media: Media) -> None:
        """Display media preview."""
        # Update info
        info_parts = [
            f"<b>{media.get_display_title()}</b>",
            f"Type: {media.media_type}",
            f"Size: {self._format_file_size(media.file_size)}",
        ]
        
        if media.width and media.height:
            info_parts.append(f"Dimensions: {media.width}×{media.height}")
        
        if media.description:
            info_parts.append(f"\n{media.description}")
        
        self.info_label.setText("\n".join(info_parts))
        
        # Update preview
        if media.media_type == "image":
            file_path = Path.cwd() / media.file_path
            if file_path.exists():
                pixmap = QPixmap(str(file_path))
                if not pixmap.isNull():
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
        elif media.media_type == "audio":
            self.preview_label.setText(f"🎵 Audio file\n\n{media.original_filename}")
        elif media.media_type == "video":
            self.preview_label.setText(f"🎬 Video file\n\n{media.original_filename}")
    
    def _on_upload_new(self) -> None:
        """Handle upload new button."""
        dialog = MediaUploadDialog(self.project_id, self.app_context, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._load_media()
    
    def _on_generate_new(self) -> None:
        """Handle generate new button."""
        # Open image generation dialog with entity context
        dialog = ImageGenerationDialog(
            app_context=self.app_context,
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            parent=self
        )
        
        if dialog.exec() == dialog.DialogCode.Accepted:
            image_path, prompt = dialog.get_result()
            
            if image_path and image_path.exists():
                try:
                    # Import the generated image into media library
                    media_id = self._import_generated_image(image_path, prompt)
                    self._load_media()
                    
                    # Select the newly created media
                    for i in range(self.media_list.count()):
                        item = self.media_list.item(i)
                        if item.data(Qt.ItemDataRole.UserRole) == media_id:
                            self.media_list.setCurrentItem(item)
                            break
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Import Error",
                        f"Failed to import generated image:\n{str(e)}"
                    )
    
    def _import_generated_image(self, source_path: Path, prompt: str) -> int:
        """Import a generated image into the media library. Returns media_id."""
        # Calculate file hash
        hasher = hashlib.sha256()
        with open(source_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()
        
        # Check for duplicates
        existing = self.app_context._session.query(Media).filter(
            Media.project_id == self.project_id,
            Media.file_hash == file_hash
        ).first()
        
        if existing:
            return existing.id
        
        # Get image dimensions
        width, height = None, None
        try:
            with Image.open(source_path) as img:
                width, height = img.size
        except Exception as e:
            print(f"Could not read image dimensions: {e}")
        
        # Determine destination path
        media_dir = Path("media") / str(self.project_id)
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
            project_id=self.project_id,
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
        
        return media.id
    
    def _on_accept(self) -> None:
        """Handle OK button click."""
        if not self.selected_media:
            QMessageBox.information(self, "No Selection", "Please select a media item to attach.")
            return
        
        try:
            # Create attachment
            caption = self.caption_input.toPlainText().strip() or None
            
            self.app_context.media_service.attach_media_to_entity(
                media_id=self.selected_media.id,
                entity_type=self.entity_type,
                entity_id=self.entity_id,
                caption=caption,
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Attachment Failed",
                f"Failed to attach media:\n\n{str(e)}"
            )
    
    def _format_file_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
