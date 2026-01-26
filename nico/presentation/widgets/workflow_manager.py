"""Workflow manager for importing and managing ComfyUI workflow presets."""
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QFileDialog,
    QTextEdit,
    QGroupBox,
    QSplitter,
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent


class WorkflowDropZone(QLabel):
    """Drop zone widget for drag-and-drop workflow import."""
    
    workflow_dropped = Signal(str)  # file path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(100)
        self._setup_style()
    
    def _setup_style(self):
        """Set up the visual style."""
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #999;
                border-radius: 8px;
                background: #f5f5f5;
                color: #666;
                padding: 20px;
                font-size: 12px;
            }
            QLabel:hover {
                border-color: #0066cc;
                background: #e8f4ff;
                color: #0066cc;
            }
        """)
        self.setText(
            "📥 Drop ComfyUI Workflow JSON Here\n\n"
            "or click 'Browse' button below"
        )
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().endswith('.json') for url in urls):
                event.acceptProposedAction()
                self.setStyleSheet("""
                    QLabel {
                        border: 2px solid #0066cc;
                        border-radius: 8px;
                        background: #cce5ff;
                        color: #0066cc;
                        padding: 20px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave."""
        self._setup_style()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop."""
        urls = event.mimeData().urls()
        json_files = [url.toLocalFile() for url in urls if url.toLocalFile().endswith('.json')]
        
        if json_files:
            for file_path in json_files:
                self.workflow_dropped.emit(file_path)
            event.acceptProposedAction()
        
        self._setup_style()


class WorkflowManagerDialog(QDialog):
    """Dialog for managing ComfyUI workflow presets."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.presets_dir = Path(__file__).parent.parent.parent.parent / "comfyui_presets"
        self.presets_dir.mkdir(exist_ok=True)
        
        self.setWindowTitle("🎨 ComfyUI Workflow Manager")
        self.setMinimumSize(900, 600)
        
        self._setup_ui()
        self._load_workflows()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Info label
        info = QLabel(
            "Manage ComfyUI workflow presets. Import new workflows by dropping JSON files "
            "or browsing, then select a workflow to view its details."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; padding: 8px; font-size: 11px;")
        layout.addWidget(info)
        
        # Drop zone
        self.drop_zone = WorkflowDropZone()
        self.drop_zone.workflow_dropped.connect(self._import_workflow)
        layout.addWidget(self.drop_zone)
        
        # Import buttons
        button_row = QHBoxLayout()
        
        self.browse_btn = QPushButton("📁 Browse for Workflow...")
        self.browse_btn.clicked.connect(self._browse_workflow)
        button_row.addWidget(self.browse_btn)
        
        button_row.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._load_workflows)
        button_row.addWidget(self.refresh_btn)
        
        layout.addLayout(button_row)
        
        # Splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Workflow list
        list_group = QGroupBox("Available Workflows")
        list_layout = QVBoxLayout()
        
        self.workflow_list = QListWidget()
        self.workflow_list.itemClicked.connect(self._preview_workflow)
        list_layout.addWidget(self.workflow_list)
        
        # List actions
        list_actions = QHBoxLayout()
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self._delete_workflow)
        self.delete_btn.setEnabled(False)
        list_actions.addWidget(self.delete_btn)
        
        self.export_btn = QPushButton("💾 Export...")
        self.export_btn.clicked.connect(self._export_workflow)
        self.export_btn.setEnabled(False)
        list_actions.addWidget(self.export_btn)
        
        list_actions.addStretch()
        list_layout.addLayout(list_actions)
        
        list_group.setLayout(list_layout)
        splitter.addWidget(list_group)
        
        # Preview area
        preview_group = QGroupBox("Workflow Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Select a workflow to preview its JSON content...")
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        splitter.addWidget(preview_group)
        
        splitter.setSizes([350, 550])
        layout.addWidget(splitter)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def _load_workflows(self):
        """Load available workflows from presets directory."""
        self.workflow_list.clear()
        
        if not self.presets_dir.exists():
            return
        
        workflows = sorted(self.presets_dir.glob("*.json"))
        
        for workflow_path in workflows:
            # Try to load and get basic info
            try:
                with open(workflow_path, 'r') as f:
                    data = json.load(f)
                
                # Count nodes
                node_count = len(data) if isinstance(data, dict) else 0
                
                item = QListWidgetItem(f"📄 {workflow_path.name}")
                item.setData(Qt.ItemDataRole.UserRole, str(workflow_path))
                item.setToolTip(f"{workflow_path.name}\n{node_count} nodes")
                
                self.workflow_list.addItem(item)
                
            except Exception as e:
                print(f"Error loading {workflow_path}: {e}")
        
        # Show count
        count = self.workflow_list.count()
        self.setWindowTitle(f"🎨 ComfyUI Workflow Manager ({count} workflow{'s' if count != 1 else ''})")
    
    def _browse_workflow(self):
        """Browse for a workflow file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ComfyUI Workflow JSON",
            str(Path.home()),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self._import_workflow(file_path)
    
    def _import_workflow(self, source_path: str):
        """Import a workflow from external file."""
        source = Path(source_path)
        
        if not source.exists():
            QMessageBox.warning(self, "File Not Found", f"File does not exist:\n{source_path}")
            return
        
        # Validate JSON
        try:
            with open(source, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                QMessageBox.warning(
                    self,
                    "Invalid Workflow",
                    "The JSON file doesn't appear to be a valid ComfyUI workflow.\n\n"
                    "Expected a JSON object/dictionary."
                )
                return
            
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self,
                "Invalid JSON",
                f"Failed to parse JSON:\n\n{e}"
            )
            return
        
        # Determine destination name
        dest_name = source.name
        dest_path = self.presets_dir / dest_name
        
        # Check if exists
        if dest_path.exists():
            reply = QMessageBox.question(
                self,
                "Workflow Exists",
                f"A workflow named '{dest_name}' already exists.\n\n"
                "Do you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Copy file
        try:
            shutil.copy2(source, dest_path)
            
            QMessageBox.information(
                self,
                "Workflow Imported",
                f"✓ Successfully imported:\n{dest_name}\n\n"
                f"Nodes: {len(data)}"
            )
            
            self._load_workflows()
            
            # Select the new item
            for i in range(self.workflow_list.count()):
                item = self.workflow_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == str(dest_path):
                    self.workflow_list.setCurrentItem(item)
                    self._preview_workflow(item)
                    break
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import workflow:\n\n{e}"
            )
    
    def _preview_workflow(self, item: QListWidgetItem):
        """Preview selected workflow."""
        workflow_path = Path(item.data(Qt.ItemDataRole.UserRole))
        
        try:
            with open(workflow_path, 'r') as f:
                data = json.load(f)
            
            # Format nicely
            preview_text = json.dumps(data, indent=2)
            self.preview_text.setPlainText(preview_text)
            
            # Enable actions
            self.delete_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
            
        except Exception as e:
            self.preview_text.setPlainText(f"Error loading workflow:\n{e}")
            self.delete_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
    
    def _delete_workflow(self):
        """Delete selected workflow."""
        current = self.workflow_list.currentItem()
        if not current:
            return
        
        workflow_path = Path(current.data(Qt.ItemDataRole.UserRole))
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this workflow?\n\n{workflow_path.name}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                workflow_path.unlink()
                QMessageBox.information(self, "Deleted", f"✓ Deleted: {workflow_path.name}")
                self._load_workflows()
                self.preview_text.clear()
                self.delete_btn.setEnabled(False)
                self.export_btn.setEnabled(False)
                
            except Exception as e:
                QMessageBox.critical(self, "Delete Failed", f"Failed to delete:\n\n{e}")
    
    def _export_workflow(self):
        """Export selected workflow to external location."""
        current = self.workflow_list.currentItem()
        if not current:
            return
        
        workflow_path = Path(current.data(Qt.ItemDataRole.UserRole))
        
        dest_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Workflow",
            str(Path.home() / workflow_path.name),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if dest_path:
            try:
                shutil.copy2(workflow_path, dest_path)
                QMessageBox.information(
                    self,
                    "Exported",
                    f"✓ Workflow exported to:\n{dest_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export:\n\n{e}")


def get_workflow_path(workflow_name: str) -> Path:
    """Get the path to a workflow preset by name.
    
    Args:
        workflow_name: Name of the workflow file (e.g., 'image_z_image_turbo.json')
    
    Returns:
        Path to the workflow file in comfyui_presets/
    """
    presets_dir = Path(__file__).parent.parent.parent.parent / "comfyui_presets"
    return presets_dir / workflow_name
