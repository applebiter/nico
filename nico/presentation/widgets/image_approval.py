"""AI-powered image approval workflow for character portraits."""
import asyncio
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QGroupBox, QProgressBar, QWidget, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap

from nico.ai.model_manager import get_model_manager


class ImageApprovalWorker(QThread):
    """Worker thread for AI image approval."""
    
    approval_complete = Signal(bool, str, int)  # approved, reason, quality_score
    error_occurred = Signal(str)
    
    def __init__(self, image_path: str, context: str, criteria: Optional[str] = None):
        super().__init__()
        self.image_path = image_path
        self.context = context
        self.criteria = criteria
    
    def run(self):
        """Run approval in background."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            manager = get_model_manager()
            approved, reason = loop.run_until_complete(
                manager.approve_image(self.image_path, self.context, self.criteria)
            )
            
            # Extract quality score if available
            quality_score = 0
            if isinstance(reason, dict):
                quality_score = reason.get('quality_score', 0)
                reason = reason.get('reason', str(reason))
            
            self.approval_complete.emit(approved, reason, quality_score)
            loop.close()
        except Exception as e:
            self.error_occurred.emit(str(e))


class ImageApprovalDialog(QDialog):
    """Dialog for AI-powered image approval."""
    
    approved = Signal(str)  # Emits image path when approved
    rejected = Signal(str, str)  # Emits image path and reason when rejected
    
    def __init__(self, image_path: str, context: str, criteria: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.context = context
        self.criteria = criteria
        self.approval_result = None
        
        self.setWindowTitle("AI Image Approval")
        self.setMinimumSize(600, 700)
        
        self._setup_ui()
        self._start_approval()
    
    def _setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout()
        
        # Image preview
        image_group = QGroupBox("Generated Image")
        image_layout = QVBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(300)
        
        # Load and display image
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(550, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText("Failed to load image")
        
        image_layout.addWidget(self.image_label)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        # Context info
        context_group = QGroupBox("Context")
        context_layout = QVBoxLayout()
        
        context_text = QLabel(self.context)
        context_text.setWordWrap(True)
        context_layout.addWidget(context_text)
        
        if self.criteria:
            criteria_label = QLabel(f"<b>Criteria:</b> {self.criteria}")
            criteria_label.setWordWrap(True)
            context_layout.addWidget(criteria_label)
        
        context_group.setLayout(context_layout)
        layout.addWidget(context_group)
        
        # AI Analysis section
        analysis_group = QGroupBox("AI Analysis")
        analysis_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        analysis_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Analyzing with vision model...")
        self.status_label.setWordWrap(True)
        analysis_layout.addWidget(self.status_label)
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMaximumHeight(120)
        self.analysis_text.hide()
        analysis_layout.addWidget(self.analysis_text)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.regenerate_btn = QPushButton("🔄 Regenerate")
        self.regenerate_btn.setEnabled(False)
        self.regenerate_btn.clicked.connect(self._on_regenerate)
        button_layout.addWidget(self.regenerate_btn)
        
        self.override_reject_btn = QPushButton("✗ Override & Reject")
        self.override_reject_btn.setEnabled(False)
        self.override_reject_btn.clicked.connect(self._on_override_reject)
        button_layout.addWidget(self.override_reject_btn)
        
        self.override_accept_btn = QPushButton("✓ Override & Accept")
        self.override_accept_btn.setEnabled(False)
        self.override_accept_btn.clicked.connect(self._on_override_accept)
        button_layout.addWidget(self.override_accept_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _start_approval(self):
        """Start AI approval process."""
        self.worker = ImageApprovalWorker(self.image_path, self.context, self.criteria)
        self.worker.approval_complete.connect(self._on_approval_complete)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()
    
    def _on_approval_complete(self, approved: bool, reason: str, quality_score: int):
        """Handle approval completion."""
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        
        self.approval_result = (approved, reason, quality_score)
        
        # Update UI
        if approved:
            self.status_label.setText(f"✅ <b>APPROVED</b> (Quality: {quality_score}/10)")
            self.status_label.setStyleSheet("color: green; font-size: 14px;")
        else:
            self.status_label.setText(f"❌ <b>REJECTED</b> (Quality: {quality_score}/10)")
            self.status_label.setStyleSheet("color: red; font-size: 14px;")
        
        self.analysis_text.setText(reason)
        self.analysis_text.show()
        
        # Enable buttons
        self.regenerate_btn.setEnabled(True)
        self.override_reject_btn.setEnabled(True)
        self.override_accept_btn.setEnabled(True)
        
        # Auto-accept if approved with high quality
        if approved and quality_score >= 7:
            self._on_override_accept()
    
    def _on_error(self, error: str):
        """Handle error."""
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        
        self.status_label.setText(f"⚠️ Error: {error}")
        self.status_label.setStyleSheet("color: orange;")
        
        self.regenerate_btn.setEnabled(True)
        self.override_accept_btn.setEnabled(True)
    
    def _on_regenerate(self):
        """Regenerate the image."""
        self.rejected.emit(self.image_path, "User requested regeneration")
        self.reject()
    
    def _on_override_reject(self):
        """Override AI and reject."""
        reason = self.approval_result[1] if self.approval_result else "User override"
        self.rejected.emit(self.image_path, f"Override rejection: {reason}")
        self.reject()
    
    def _on_override_accept(self):
        """Override AI and accept."""
        self.approved.emit(self.image_path)
        self.accept()


class BatchImageApprovalWidget(QWidget):
    """Widget for batch approval of multiple images."""
    
    all_complete = Signal(list, list)  # approved_paths, rejected_paths
    
    def __init__(self, image_paths: list[str], context: str, criteria: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.image_paths = image_paths
        self.context = context
        self.criteria = criteria
        self.approved_images = []
        self.rejected_images = []
        self.current_index = 0
        
        self.setWindowTitle("Batch Image Approval")
        self.setMinimumSize(700, 800)
        
        self._setup_ui()
        self._process_next()
    
    def _setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout()
        
        # Progress header
        self.header_label = QLabel()
        self.header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.header_label)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setMaximum(len(self.image_paths))
        layout.addWidget(self.overall_progress)
        
        # Scroll area for current image
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        scroll.setWidget(self.content_widget)
        
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def _update_header(self):
        """Update progress header."""
        total = len(self.image_paths)
        self.header_label.setText(
            f"Processing Image {self.current_index + 1} of {total} "
            f"(✓ {len(self.approved_images)} approved, ✗ {len(self.rejected_images)} rejected)"
        )
        self.overall_progress.setValue(self.current_index)
    
    def _process_next(self):
        """Process next image."""
        if self.current_index >= len(self.image_paths):
            self._on_batch_complete()
            return
        
        self._update_header()
        
        image_path = self.image_paths[self.current_index]
        
        # Create approval dialog
        dialog = ImageApprovalDialog(image_path, self.context, self.criteria, self)
        dialog.approved.connect(self._on_image_approved)
        dialog.rejected.connect(self._on_image_rejected)
        dialog.exec()
    
    def _on_image_approved(self, image_path: str):
        """Handle approved image."""
        self.approved_images.append(image_path)
        self.current_index += 1
        self._process_next()
    
    def _on_image_rejected(self, image_path: str, reason: str):
        """Handle rejected image."""
        self.rejected_images.append((image_path, reason))
        self.current_index += 1
        self._process_next()
    
    def _on_batch_complete(self):
        """Handle batch completion."""
        self.header_label.setText(
            f"✨ Batch Complete! {len(self.approved_images)} approved, {len(self.rejected_images)} rejected"
        )
        self.all_complete.emit(self.approved_images, [r[0] for r in self.rejected_images])
