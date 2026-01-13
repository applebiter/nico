"""Entry point for Nico application."""
# Import config first to disable telemetry before any other imports
from nico import config  # noqa: F401

import sys

from PySide6.QtWidgets import QApplication

from nico.presentation.main_window import MainWindow


def main() -> int:
    """Main entry point for the application."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Nico")
    app.setOrganizationName("Applebiter")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
