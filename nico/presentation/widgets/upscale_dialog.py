"""Dialog for selecting upscale resolution presets."""
from pathlib import Path
from typing import Optional, Tuple
from math import gcd

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QDialogButtonBox,
    QGroupBox,
)
from PySide6.QtGui import QPixmap


class UpscaleDialog(QDialog):
    """Dialog for selecting upscale resolution from presets matching aspect ratio."""
    
    # Common upscale presets (width, height, name)
    PRESETS = [
        # HD/FHD 16:9
        (1920, 1080, "Full HD (1920×1080) - 16:9"),
        (2560, 1440, "2K QHD (2560×1440) - 16:9"),
        (3840, 2160, "4K UHD (3840×2160) - 16:9"),
        
        # Portrait 9:16
        (1080, 1920, "Full HD Portrait (1080×1920) - 9:16"),
        (1440, 2560, "2K Portrait (1440×2560) - 9:16"),
        (2160, 3840, "4K Portrait (2160×3840) - 9:16"),
        
        # Square 1:1
        (2048, 2048, "2K Square (2048×2048) - 1:1"),
        (3072, 3072, "3K Square (3072×3072) - 1:1"),
        (4096, 4096, "4K Square (4096×4096) - 1:1"),
        
        # Cinematic 21:9
        (2560, 1080, "Ultrawide FHD (2560×1080) - 21:9"),
        (3440, 1440, "Ultrawide QHD (3440×1440) - 21:9"),
        (5120, 2160, "Ultrawide 4K (5120×2160) - 21:9"),
        
        # 4:3 Classic
        (2048, 1536, "2K Classic (2048×1536) - 4:3"),
        (2560, 1920, "HD+ Classic (2560×1920) - 4:3"),
        (4096, 3072, "4K Classic (4096×3072) - 4:3"),
        
        # 3:2 Photography
        (3000, 2000, "Photography (3000×2000) - 3:2"),
        (4500, 3000, "Photography HD (4500×3000) - 3:2"),
        (6000, 4000, "Photography 4K (6000×4000) - 3:2"),
        
        # 5:4 Portrait-ish
        (2048, 1638, "Portrait-ish (2048×1638) - 5:4"),
        (2560, 2048, "Portrait-ish HD (2560×2048) - 5:4"),
        (4096, 3277, "Portrait-ish 4K (4096×3277) - 5:4"),
    ]
    
    def __init__(self, image_path: Path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.selected_width = None
        self.selected_height = None
        
        # Get image dimensions
        pixmap = QPixmap(str(image_path))
        self.current_width = pixmap.width()
        self.current_height = pixmap.height()
        
        self.setWindowTitle("Upscale Image")
        self.setModal(True)
        self.resize(500, 600)
        
        self._setup_ui()
        self._populate_presets()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Current image info
        info_group = QGroupBox("Current Image")
        info_layout = QVBoxLayout()
        
        aspect_ratio = self._calculate_aspect_ratio(self.current_width, self.current_height)
        info_label = QLabel(
            f"📐 Dimensions: {self.current_width}×{self.current_height}\n"
            f"📊 Aspect Ratio: {aspect_ratio}"
        )
        info_layout.addWidget(info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Preset list
        preset_group = QGroupBox("Select Target Resolution")
        preset_layout = QVBoxLayout()
        
        help_label = QLabel(
            "💡 Presets are ordered by aspect ratio match.\n"
            "Choose a resolution that preserves your image's proportions."
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #888; font-style: italic;")
        preset_layout.addWidget(help_label)
        
        self.preset_list = QListWidget()
        self.preset_list.itemDoubleClicked.connect(self._on_preset_double_clicked)
        preset_layout.addWidget(self.preset_list)
        
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def _calculate_aspect_ratio(self, width: int, height: int) -> str:
        """Calculate aspect ratio in simplified form."""
        divisor = gcd(width, height)
        ratio_w = width // divisor
        ratio_h = height // divisor
        
        # Check for common aspect ratios
        common_ratios = {
            (16, 9): "16:9",
            (9, 16): "9:16",
            (1, 1): "1:1",
            (4, 3): "4:3",
            (3, 2): "3:2",
            (21, 9): "21:9",
            (5, 4): "5:4",
            (832, 1216): "~2:3",
            (896, 1152): "~7:9",
        }
        
        ratio_tuple = (ratio_w, ratio_h)
        if ratio_tuple in common_ratios:
            return common_ratios[ratio_tuple]
        
        return f"{ratio_w}:{ratio_h}"
    
    def _aspect_ratio_difference(self, width: int, height: int) -> float:
        """Calculate how different a resolution is from the current aspect ratio."""
        current_ratio = self.current_width / self.current_height
        preset_ratio = width / height
        return abs(current_ratio - preset_ratio)
    
    def _populate_presets(self) -> None:
        """Populate the preset list, sorted by aspect ratio match."""
        # Filter presets that are larger than current image
        valid_presets = [
            (w, h, name) for w, h, name in self.PRESETS
            if w >= self.current_width or h >= self.current_height
        ]
        
        # Sort by aspect ratio similarity
        sorted_presets = sorted(
            valid_presets,
            key=lambda p: self._aspect_ratio_difference(p[0], p[1])
        )
        
        # Add items to list
        for width, height, name in sorted_presets:
            diff = self._aspect_ratio_difference(width, height)
            
            # Mark perfect or near-perfect matches
            if diff < 0.01:
                prefix = "✓ "
                style = "font-weight: bold;"
            elif diff < 0.05:
                prefix = "• "
                style = ""
            else:
                prefix = "  "
                style = "color: #888;"
            
            item = QListWidgetItem(f"{prefix}{name}")
            item.setData(Qt.ItemDataRole.UserRole, (width, height))
            
            if style:
                item.setForeground(Qt.GlobalColor.white if "bold" in style else Qt.GlobalColor.gray)
            
            self.preset_list.addItem(item)
        
        # Select first item by default
        if self.preset_list.count() > 0:
            self.preset_list.setCurrentRow(0)
    
    def _on_preset_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on preset - accept immediately."""
        self.accept()
    
    def accept(self) -> None:
        """Handle dialog acceptance."""
        current_item = self.preset_list.currentItem()
        if current_item:
            self.selected_width, self.selected_height = current_item.data(Qt.ItemDataRole.UserRole)
        super().accept()
    
    def get_selected_resolution(self) -> Optional[Tuple[int, int]]:
        """Get the selected resolution, or None if dialog was cancelled."""
        if self.selected_width and self.selected_height:
            return (self.selected_width, self.selected_height)
        return None
