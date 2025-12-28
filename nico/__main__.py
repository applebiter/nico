"""Main entry point for the nico application."""

import sys

# Disable all telemetry FIRST, before any other imports
from nico.config import disable_telemetry
disable_telemetry()

from PySide6.QtWidgets import QApplication

from nico.presentation.ui.main_window import MainWindow


def main() -> int:
    """Initialize and run the nico application."""
    app = QApplication(sys.argv)
    app.setApplicationName("nico")
    app.setOrganizationName("nico")
    app.setApplicationVersion("0.1.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
