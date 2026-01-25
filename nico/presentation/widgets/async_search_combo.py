"""Async searchable combo box for large datasets."""
from typing import Optional, Callable
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import QComboBox, QLineEdit


class AsyncSearchComboBox(QComboBox):
    """Combo box that searches database asynchronously as user types.
    
    Instead of loading all items upfront, this widget:
    1. Waits for user to type
    2. Queries database for matches
    3. Shows limited results (default 100)
    
    This keeps the UI responsive even with huge datasets (5000+ items).
    """
    
    textChanged = Signal(str)
    
    def __init__(self, parent=None, search_func: Optional[Callable[[str, int], list[str]]] = None):
        """Initialize async search combo.
        
        Args:
            parent: Parent widget
            search_func: Function that takes (query: str, limit: int) and returns list of matches
        """
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        self._search_func = search_func
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)
        self._search_delay_ms = 300  # Wait 300ms after user stops typing
        self._max_results = 100
        self._all_items = []  # For random selection
        
        # Connect signals
        line_edit = self.lineEdit()
        if line_edit:
            line_edit.textEdited.connect(self._on_text_edited)
            line_edit.returnPressed.connect(self._on_return_pressed)
        
        # When user selects from dropdown, position cursor at start
        self.activated.connect(self._on_item_selected)
    
    def set_search_function(self, func: Callable[[str, int], list[str]]) -> None:
        """Set the search function."""
        self._search_func = func
    
    def set_all_items(self, items: list[str]) -> None:
        """Set all items for random selection (without adding to combo)."""
        self._all_items = items
    
    def get_random_item(self) -> Optional[str]:
        """Get a random item from the full dataset."""
        if not self._all_items:
            return None
        import random
        return random.choice(self._all_items)
    
    def _on_text_edited(self, text: str) -> None:
        """Handle text being edited (user typing)."""
        # Restart the timer - only search after user stops typing
        self._search_timer.stop()
        self._search_timer.start(self._search_delay_ms)
    
    def _on_return_pressed(self) -> None:
        """Handle return key - accept current text."""
        self.hidePopup()
    
    def _on_item_selected(self) -> None:
        """Handle item selection from dropdown - show text from beginning."""
        line_edit = self.lineEdit()
        if line_edit:
            # Move cursor to start so long text is visible from beginning
            line_edit.home(False)  # False = don't select text
    
    def _perform_search(self) -> None:
        """Perform the actual search."""
        if not self._search_func:
            return
        
        query = self.currentText()
        
        # Don't search for very short queries
        if len(query) < 2:
            self.clear()
            return
        
        # Get matches from search function
        matches = self._search_func(query, self._max_results)
        
        # Update combo box
        self.clear()
        if matches:
            self.addItems(matches)
            self.showPopup()
        
        # Restore user's text (addItems may have changed it)
        self.setEditText(query)
        
        # Move cursor to home position so long text shows from the beginning
        line_edit = self.lineEdit()
        if line_edit:
            line_edit.setCursorPosition(len(query))
    
    def currentText(self) -> str:
        """Get current text."""
        return super().currentText()
    
    def setText(self, text: str) -> None:
        """Set text."""
        self.setEditText(text)
