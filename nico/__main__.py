"""Entry point for Nico application."""
# Import config first to disable telemetry before any other imports
from nico import config  # noqa: F401

import sys
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineCore import QWebEngineSettings

from nico.presentation.main_window import MainWindow


def main() -> int:
    """Main entry point for the application."""
    # Set Qt WebEngine to use software rendering to avoid GPU issues
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu --no-sandbox --disable-dev-shm-usage'
    
    # Enable software rendering
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL)
    
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
