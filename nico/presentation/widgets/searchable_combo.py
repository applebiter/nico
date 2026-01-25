"""Searchable combo box widget for large lists."""
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QCompleter, QLineEdit


class SearchableComboBox(QComboBox):
    """Combo box with built-in search/filter functionality.
    
    Ideal for large lists like occupations (5000+ items).
    """
    
    textChanged = Signal(str)  # Emitted when text changes (typed or selected)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        # Set up completer for auto-complete
        self.completer_obj = QCompleter()
        self.completer_obj.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer_obj.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer_obj.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCompleter(self.completer_obj)
        
        # Connect signals
        self.currentTextChanged.connect(self._on_text_changed)
        line_edit = self.lineEdit()
        if line_edit:
            line_edit.textChanged.connect(self._on_line_edit_changed)
    
    def setItems(self, items: List[str], sort: bool = True) -> None:
        """Set the list of items.
        
        Args:
            items: List of items to populate
            sort: Whether to sort alphabetically (default True)
        """
        self.clear()
        
        if sort:
            items = sorted(items, key=str.lower)
        
        self.addItems(items)
        
        # Update completer model
        if self.completer_obj:
            self.completer_obj.setModel(self.model())
    
    def currentText(self) -> str:
        """Get current text (from selection or manual entry)."""
        return super().currentText()
    
    def setText(self, text: str) -> None:
        """Set text (finds in list or allows custom entry)."""
        index = self.findText(text, Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)
        else:
            self.setEditText(text)
    
    def _on_text_changed(self, text: str) -> None:
        """Internal handler for text changes."""
        self.textChanged.emit(text)
    
    def _on_line_edit_changed(self, text: str) -> None:
        """Handle manual typing in line edit."""
        # Allow filtering while typing
        pass


class RandomizableComboBox(SearchableComboBox):
    """Searchable combo box with a randomize button."""
    
    randomClicked = Signal()
    
    def __init__(self, parent=None, show_random_button: bool = True):
        super().__init__(parent)
        self.show_random_button = show_random_button
        self._items_list = []
    
    def setItems(self, items: List[str], sort: bool = True) -> None:
        """Set items and store for randomization."""
        self._items_list = list(items)
        super().setItems(items, sort)
    
    def randomize(self) -> str:
        """Pick a random item from the list."""
        if not self._items_list:
            return ""
        
        import random
        item = random.choice(self._items_list)
        self.setText(item)
        return item
