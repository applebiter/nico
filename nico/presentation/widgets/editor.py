"""Editor widget - main writing surface."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLabel,
    QToolBar,
    QPushButton,
    QComboBox,
)
from PySide6.QtGui import QFont


class EditorWidget(QWidget):
    """Center panel: Rich text editor for scenes."""
    
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the widget layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header with scene info
        header = QHBoxLayout()
        self.scene_title = QLabel("✍️ Morning in the Tower")
        self.scene_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(self.scene_title)
        
        header.addStretch()
        
        self.word_count = QLabel("1,250 words")
        self.word_count.setStyleSheet("color: #666;")
        header.addWidget(self.word_count)
        
        layout.addLayout(header)
        
        # Formatting toolbar (placeholder)
        toolbar = QToolBar()
        toolbar.addAction("B", self._on_bold)
        toolbar.addAction("I", self._on_italic)
        toolbar.addAction("U", self._on_underline)
        toolbar.addSeparator()
        
        # Font size combo
        font_size = QComboBox()
        font_size.addItems(["10", "12", "14", "16", "18", "20", "24"])
        font_size.setCurrentText("14")
        toolbar.addWidget(font_size)
        
        layout.addWidget(toolbar)
        
        # Text editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Start writing your scene here...")
        
        # Set a nice writing font
        font = QFont("Georgia", 14)
        self.editor.setFont(font)
        
        # Sample content
        self.editor.setHtml("""
        <p>Elara gazed out the tower window as dawn broke over the mountains. 
        The first rays of sunlight painted the peaks in shades of gold and rose, 
        a sight that never failed to take her breath away.</p>
        
        <p>Five years she had lived in the Ivory Tower, studying under Master Theron's 
        watchful eye. Five years of learning the ancient arts, of memorizing spells 
        and incantations, of practicing the delicate balance between power and control.</p>
        
        <p>"You're up early," came a familiar voice from the doorway.</p>
        
        <p>She turned to see Master Theron, his silver hair catching the morning light. 
        Despite his advanced age, his green eyes were sharp and alert.</p>
        
        <p>"I couldn't sleep," Elara admitted. "Today's the day of the examination."</p>
        """)
        
        layout.addWidget(self.editor)
        
        # Footer with scene metadata
        footer = QHBoxLayout()
        footer.addWidget(QLabel("Beat: Opening image"))
        footer.addStretch()
        footer.addWidget(QLabel("POV: Elara"))
        footer.addWidget(QLabel("Setting: Mage Tower"))
        
        layout.addLayout(footer)
        
        self.setLayout(layout)
        
    # Formatting action handlers (placeholders)
    def _on_bold(self) -> None:
        """Toggle bold formatting."""
        pass
        
    def _on_italic(self) -> None:
        """Toggle italic formatting."""
        pass
        
    def _on_underline(self) -> None:
        """Toggle underline formatting."""
        pass
