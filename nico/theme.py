"""Theme definitions for dark and light modes."""
from typing import Dict


class Theme:
    """Theme color definitions."""
    
    @staticmethod
    def get_dark_theme() -> str:
        """Get dark theme stylesheet."""
        return """
            /* Main Window */
            QMainWindow {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            
            /* Menus */
            QMenuBar {
                background-color: #252526;
                color: #d4d4d4;
                border-bottom: 1px solid #3e3e42;
            }
            QMenuBar::item:selected {
                background-color: #2a2d2e;
            }
            QMenu {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            
            /* Widgets */
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            
            /* Text Edits */
            QTextEdit, QLineEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 2px;
                padding: 4px;
                selection-background-color: #264f78;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                border-radius: 2px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d4f7c;
            }
            QPushButton:checked {
                background-color: #094771;
            }
            QPushButton:disabled {
                background-color: #3e3e42;
                color: #6e6e6e;
            }
            
            /* Tree Widget (Binder) */
            QTreeWidget {
                background-color: #252526;
                color: #d4d4d4;
                border: none;
                outline: none;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
            }
            QTreeWidget::item:hover {
                background-color: #2a2d2e;
            }
            
            /* List Widget */
            QListWidget {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #094771;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
            
            /* Group Box */
            QGroupBox {
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
            
            /* Labels */
            QLabel {
                color: #d4d4d4;
                background-color: transparent;
            }
            
            /* Scroll Bars */
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 14px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #424242;
                border-radius: 7px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4e4e4e;
            }
            QScrollBar:horizontal {
                background-color: #1e1e1e;
                height: 14px;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background-color: #424242;
                border-radius: 7px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #4e4e4e;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                border: none;
                background: none;
            }
            
            /* Tab Widget */
            QTabWidget::pane {
                border: 1px solid #3e3e42;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #969696;
                padding: 8px 16px;
                border: 1px solid #3e3e42;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QTabBar::tab:hover {
                background-color: #2a2d2e;
            }
            
            /* Combo Box */
            QComboBox {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 2px;
                padding: 4px 8px;
            }
            QComboBox:hover {
                background-color: #464646;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #252526;
                color: #d4d4d4;
                selection-background-color: #094771;
            }
            
            /* Tool Bar */
            QToolBar {
                background-color: #2d2d30;
                border: none;
                spacing: 4px;
            }
            QToolButton {
                background-color: transparent;
                color: #d4d4d4;
                border: none;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: #3e3e42;
            }
            QToolButton:pressed {
                background-color: #094771;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #007acc;
                color: #ffffff;
            }
            
            /* Splitter */
            QSplitter::handle {
                background-color: #3e3e42;
            }
            QSplitter::handle:hover {
                background-color: #007acc;
            }
        """
    
    @staticmethod
    def get_light_theme() -> str:
        """Get light theme stylesheet."""
        return """
            /* Main Window */
            QMainWindow {
                background-color: #ffffff;
                color: #000000;
            }
            
            /* Menus */
            QMenuBar {
                background-color: #f3f3f3;
                color: #000000;
                border-bottom: 1px solid #d4d4d4;
            }
            QMenuBar::item:selected {
                background-color: #e5e5e5;
            }
            QMenu {
                background-color: #f3f3f3;
                color: #000000;
                border: 1px solid #d4d4d4;
            }
            QMenu::item:selected {
                background-color: #cce8ff;
            }
            
            /* Widgets */
            QWidget {
                background-color: #ffffff;
                color: #000000;
            }
            
            /* Text Edits */
            QTextEdit, QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #d4d4d4;
                border-radius: 2px;
                padding: 4px;
                selection-background-color: #add6ff;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 2px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:checked {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
            
            /* Tree Widget (Binder) */
            QTreeWidget {
                background-color: #f3f3f3;
                color: #000000;
                border: none;
                outline: none;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #cce8ff;
            }
            QTreeWidget::item:hover {
                background-color: #e5e5e5;
            }
            
            /* List Widget */
            QListWidget {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #d4d4d4;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e5e5e5;
            }
            QListWidget::item:selected {
                background-color: #cce8ff;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
            
            /* Group Box */
            QGroupBox {
                color: #000000;
                border: 1px solid #d4d4d4;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
            
            /* Labels */
            QLabel {
                color: #000000;
                background-color: transparent;
            }
            
            /* Scroll Bars */
            QScrollBar:vertical {
                background-color: #f3f3f3;
                width: 14px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 7px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
            QScrollBar:horizontal {
                background-color: #f3f3f3;
                height: 14px;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background-color: #c1c1c1;
                border-radius: 7px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #a8a8a8;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                border: none;
                background: none;
            }
            
            /* Tab Widget */
            QTabWidget::pane {
                border: 1px solid #d4d4d4;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #e5e5e5;
                color: #666666;
                padding: 8px 16px;
                border: 1px solid #d4d4d4;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #000000;
            }
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            
            /* Combo Box */
            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #d4d4d4;
                border-radius: 2px;
                padding: 4px 8px;
            }
            QComboBox:hover {
                background-color: #f0f0f0;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #cce8ff;
            }
            
            /* Tool Bar */
            QToolBar {
                background-color: #f3f3f3;
                border: none;
                spacing: 4px;
            }
            QToolButton {
                background-color: transparent;
                color: #000000;
                border: none;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: #e5e5e5;
            }
            QToolButton:pressed {
                background-color: #cce8ff;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            /* Splitter */
            QSplitter::handle {
                background-color: #d4d4d4;
            }
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
        """
