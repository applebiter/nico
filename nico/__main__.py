"""Main entry point for the nico application."""

import sys

# Disable all telemetry FIRST, before any other imports
from nico.config import disable_telemetry
disable_telemetry()

from PySide6.QtWidgets import QApplication


def main():
    """Initialize and run the nico application."""
    app = QApplication(sys.argv)
    app.setApplicationName("nico")
    app.setOrganizationName("nico")
    app.setApplicationVersion("0.1.0")
    
    # TODO: Initialize main window
    print("nico - Narrative Insight Composition Output")
    print("Application structure initialized. Main window coming soon...")
    
    return 0  # Temporary exit until we have a main window


if __name__ == "__main__":
    sys.exit(main())
