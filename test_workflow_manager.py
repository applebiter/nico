#!/usr/bin/env python3
"""Test the ComfyUI Workflow Manager."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from nico.presentation.widgets.workflow_manager import WorkflowManagerDialog


def main():
    """Run the workflow manager test."""
    print("=" * 60)
    print("COMFYUI WORKFLOW MANAGER TEST")
    print("=" * 60)
    print()
    print("This dialog lets you manage ComfyUI workflow presets:")
    print()
    print("Features:")
    print("  • 📥 Drag-and-drop JSON files onto the drop zone")
    print("  • 📁 Browse for workflow files")
    print("  • 📄 Preview workflow JSON content")
    print("  • 🗑️  Delete unwanted workflows")
    print("  • 💾 Export workflows to external location")
    print("  • 🔄 Refresh workflow list")
    print()
    print("Current workflows in comfyui_presets/:")
    
    presets_dir = Path(__file__).parent / "comfyui_presets"
    if presets_dir.exists():
        workflows = list(presets_dir.glob("*.json"))
        if workflows:
            for wf in workflows:
                print(f"  ✓ {wf.name}")
        else:
            print("  (none)")
    else:
        print("  (directory not found)")
    
    print()
    print("=" * 60)
    print()
    print("Opening Workflow Manager...")
    print()
    
    app = QApplication(sys.argv)
    dialog = WorkflowManagerDialog()
    dialog.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
