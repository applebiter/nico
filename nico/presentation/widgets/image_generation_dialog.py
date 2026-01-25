"""Image generation dialog for creating images for any entity type."""
import asyncio
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QProgressBar,
    QMessageBox,
    QDialogButtonBox,
    QGroupBox,
)
from PySide6.QtGui import QPixmap

from nico.application.context import AppContext
from nico.infrastructure.comfyui_service import get_comfyui_service


class ImageGenerationWorker(QObject):
    """Worker for generating images in a background thread."""
    finished = Signal(object)  # image_path or None
    error = Signal(str)  # error message
    
    def __init__(self, prompt: str, project_path: Path, width: int = 1024, height: int = 1024, seed: int = None):
        super().__init__()
        self.prompt = prompt
        self.project_path = project_path
        self.width = width
        self.height = height
        self.seed = seed
    
    def run(self):
        """Generate image using ComfyUI."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Get ComfyUI service and generate image
            comfyui = get_comfyui_service(project_path=self.project_path)
            image_path = loop.run_until_complete(
                comfyui.generate_image(self.prompt, width=self.width, height=self.height, seed=self.seed)
            )
            
            loop.close()
            
            self.finished.emit(image_path)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class ImageGenerationDialog(QDialog):
    """Dialog for generating images with ComfyUI."""
    
    # Signal emitted with the generated image path when accepted
    image_generated = Signal(Path, str)  # image_path, prompt
    
    def __init__(
        self,
        app_context: AppContext,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        initial_prompt: str = "",
        parent=None
    ):
        super().__init__(parent)
        self.app_context = app_context
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.generated_image_path: Optional[Path] = None
        self.generated_prompt: Optional[str] = None
        
        self.setWindowTitle("✨ Generate Image")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
        
        self._setup_ui(initial_prompt)
    
    def _setup_ui(self, initial_prompt: str) -> None:
        """Set up the dialog layout."""
        layout = QVBoxLayout()
        
        # Instructions
        info_label = QLabel(
            "Generate an image using ComfyUI (z-image-turbo). "
            "Make sure ComfyUI is running at http://127.0.0.1:8188"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(info_label)
        
        # Prompt group
        prompt_group = QGroupBox("Prompt")
        prompt_layout = QVBoxLayout()
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setAcceptRichText(False)
        self.prompt_input.setPlaceholderText(
            "Enter image generation prompt...\n\n"
            "Example: A serene mountain landscape at sunset, photorealistic, detailed"
        )
        self.prompt_input.setMinimumHeight(150)
        if initial_prompt:
            self.prompt_input.setPlainText(initial_prompt)
        prompt_layout.addWidget(self.prompt_input)
        
        # Template button if entity context available
        if self.entity_type and self.entity_id:
            template_btn = QPushButton("📝 Use Entity Description")
            template_btn.clicked.connect(self._load_entity_description)
            prompt_layout.addWidget(template_btn)
        
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)
        
        # Settings group
        settings_group = QGroupBox("Generation Settings")
        settings_layout = QFormLayout()
        
        # Dimension preset
        dimension_layout = QHBoxLayout()
        self.dimension_preset = QComboBox()
        self.dimension_preset.addItems([
            "Square 1024×1024",
            "Portrait 832×1216",
            "Landscape 1216×832",
            "Wide 1344×768",
            "Tall 768×1344",
            "Custom"
        ])
        self.dimension_preset.currentTextChanged.connect(self._on_preset_changed)
        dimension_layout.addWidget(self.dimension_preset)
        settings_layout.addRow("Preset:", dimension_layout)
        
        # Width and Height
        dimensions_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setMinimum(512)
        self.width_spin.setMaximum(2048)
        self.width_spin.setSingleStep(64)
        self.width_spin.setValue(1024)
        dimensions_layout.addWidget(QLabel("W:"))
        dimensions_layout.addWidget(self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setMinimum(512)
        self.height_spin.setMaximum(2048)
        self.height_spin.setSingleStep(64)
        self.height_spin.setValue(1024)
        dimensions_layout.addWidget(QLabel("H:"))
        dimensions_layout.addWidget(self.height_spin)
        dimensions_layout.addStretch()
        settings_layout.addRow("Dimensions:", dimensions_layout)
        
        # Seed
        seed_layout = QHBoxLayout()
        self.seed_input = QLineEdit()
        self.seed_input.setPlaceholderText("Random")
        self.seed_input.setMaximumWidth(150)
        seed_layout.addWidget(self.seed_input)
        seed_layout.addStretch()
        settings_layout.addRow("Seed:", seed_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Generated image will appear here")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background: #f5f5f5;")
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("✨ Generate")
        self.generate_btn.clicked.connect(self._on_generate)
        self.generate_btn.setDefault(True)
        button_layout.addWidget(self.generate_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.accept_btn = QPushButton("Accept")
        self.accept_btn.clicked.connect(self.accept)
        self.accept_btn.setEnabled(False)
        button_layout.addWidget(self.accept_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _on_preset_changed(self, preset: str) -> None:
        """Handle dimension preset change."""
        presets = {
            "Square 1024×1024": (1024, 1024),
            "Portrait 832×1216": (832, 1216),
            "Landscape 1216×832": (1216, 832),
            "Wide 1344×768": (1344, 768),
            "Tall 768×1344": (768, 1344),
        }
        
        if preset in presets:
            width, height = presets[preset]
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)
            self.width_spin.setEnabled(False)
            self.height_spin.setEnabled(False)
        else:  # Custom
            self.width_spin.setEnabled(True)
            self.height_spin.setEnabled(True)
    
    def _load_entity_description(self) -> None:
        """Load description from the entity."""
        if not self.entity_type or not self.entity_id:
            return
        
        try:
            entity = None
            description = ""
            
            if self.entity_type == 'character':
                from nico.domain.models import Character
                entity = self.app_context._session.query(Character).filter(
                    Character.id == self.entity_id
                ).first()
                if entity and entity.physical_description:
                    description = entity.physical_description
            
            elif self.entity_type == 'location':
                from nico.domain.models import Location
                entity = self.app_context._session.query(Location).filter(
                    Location.id == self.entity_id
                ).first()
                if entity:
                    parts = []
                    if entity.description:
                        parts.append(entity.description)
                    if entity.atmosphere:
                        parts.append(f"Atmosphere: {entity.atmosphere}")
                    description = "\n".join(parts)
            
            elif self.entity_type == 'scene':
                from nico.domain.models import Scene
                entity = self.app_context._session.query(Scene).filter(
                    Scene.id == self.entity_id
                ).first()
                if entity and entity.summary:
                    description = entity.summary
            
            elif self.entity_type in ('project', 'story', 'chapter'):
                # Get summary from meta
                model_map = {
                    'project': 'Project',
                    'story': 'Story',
                    'chapter': 'Chapter',
                }
                model_name = model_map[self.entity_type]
                Model = getattr(__import__('nico.domain.models', fromlist=[model_name]), model_name)
                entity = self.app_context._session.query(Model).filter(
                    Model.id == self.entity_id
                ).first()
                if entity and entity.meta:
                    description = entity.meta.get('summary', '') or entity.meta.get('notes', '')
            
            if description:
                self.prompt_input.setPlainText(description)
            else:
                QMessageBox.information(
                    self,
                    "No Description",
                    "This entity doesn't have a description yet."
                )
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load entity description: {e}")
    
    def _on_generate(self) -> None:
        """Generate the image."""
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "No Prompt", "Please enter a prompt for image generation.")
            return
        
        # Disable controls
        self.generate_btn.setEnabled(False)
        self.accept_btn.setEnabled(False)
        self.prompt_input.setEnabled(False)
        self.dimension_preset.setEnabled(False)
        self.width_spin.setEnabled(False)
        self.height_spin.setEnabled(False)
        self.seed_input.setEnabled(False)
        
        # Show progress
        self.progress_bar.show()
        
        # Get settings
        width = self.width_spin.value()
        height = self.height_spin.value()
        seed_text = self.seed_input.text().strip()
        seed = int(seed_text) if seed_text.isdigit() else None
        
        # Get project path
        project_path = Path.cwd()
        
        # Create worker and thread
        self.worker = ImageGenerationWorker(prompt, project_path, width, height, seed)
        self.thread = QThread()
        
        # Move worker to thread
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_image_generated)
        self.worker.error.connect(self._on_generation_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start
        self.thread.start()
    
    def _on_image_generated(self, image_path) -> None:
        """Handle successful generation."""
        # Re-enable controls
        self.generate_btn.setEnabled(True)
        self.prompt_input.setEnabled(True)
        self.dimension_preset.setEnabled(True)
        if self.dimension_preset.currentText() == "Custom":
            self.width_spin.setEnabled(True)
            self.height_spin.setEnabled(True)
        self.seed_input.setEnabled(True)
        
        # Hide progress
        self.progress_bar.hide()
        
        if image_path and image_path.exists():
            # Display preview
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                # Scale to fit preview
                scaled = pixmap.scaled(
                    400, 400,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)
                
                # Store for accept
                self.generated_image_path = image_path
                self.generated_prompt = self.prompt_input.toPlainText().strip()
                self.accept_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Error", "Failed to load generated image")
        else:
            QMessageBox.warning(
                self,
                "Generation Failed",
                "ComfyUI did not return an image. Check the console for details.\n\n"
                "Make sure ComfyUI is running at http://127.0.0.1:8188"
            )
    
    def _on_generation_failed(self, error_msg: str) -> None:
        """Handle generation failure."""
        # Re-enable controls
        self.generate_btn.setEnabled(True)
        self.prompt_input.setEnabled(True)
        self.dimension_preset.setEnabled(True)
        if self.dimension_preset.currentText() == "Custom":
            self.width_spin.setEnabled(True)
            self.height_spin.setEnabled(True)
        self.seed_input.setEnabled(True)
        
        # Hide progress
        self.progress_bar.hide()
        
        QMessageBox.critical(
            self,
            "Generation Error",
            f"Failed to generate image:\n\n{error_msg}\n\n"
            "Make sure ComfyUI is running at http://127.0.0.1:8188"
        )
    
    def accept(self) -> None:
        """Handle dialog acceptance."""
        if self.generated_image_path:
            self.image_generated.emit(self.generated_image_path, self.generated_prompt)
        super().accept()
    
    def get_result(self) -> tuple[Optional[Path], Optional[str]]:
        """Get the generated image path and prompt."""
        return (self.generated_image_path, self.generated_prompt)
