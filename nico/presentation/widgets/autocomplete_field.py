"""AI-powered autocomplete text field widget."""
from PySide6.QtWidgets import QLineEdit, QTextEdit, QCompleter
from PySide6.QtCore import QTimer, Signal, Qt, QStringListModel
from PySide6.QtGui import QTextCursor
import asyncio
from typing import Optional, Dict, Any
from nico.preferences import get_preferences


class AutocompleteLineEdit(QLineEdit):
    """Line edit with AI-powered autocomplete suggestions."""
    
    suggestion_requested = Signal(str, str)  # field_type, current_text
    
    def __init__(
        self,
        field_type: str = "text",
        parent=None,
        context: Optional[Dict[str, Any]] = None,
        debounce_ms: int = 800
    ):
        super().__init__(parent)
        self.field_type = field_type
        self.context = context or {}
        self._debounce_ms = debounce_ms
        self._suggestion_timer = QTimer()
        self._suggestion_timer.setSingleShot(True)
        self._suggestion_timer.timeout.connect(self._request_suggestion)
        self._last_text = ""
        self._pending_suggestion: Optional[str] = None
        
        # Setup completer for showing suggestions
        self._completer = QCompleter()
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self._completer.activated.connect(self._insert_completion)
        
        # Connect text changes to trigger suggestions
        self.textChanged.connect(self._on_text_changed)
    
    def _on_text_changed(self, text: str):
        """Handle text changes with debouncing."""
        # Check if autocomplete is enabled
        if not get_preferences().autocomplete_enabled:
            return
        
        # Only trigger if text is growing and substantial
        if len(text) >= 3 and len(text) > len(self._last_text):
            self._suggestion_timer.start(self._debounce_ms)
        else:
            self._suggestion_timer.stop()
        
        self._last_text = text
    
    def _request_suggestion(self):
        """Request AI suggestion for current text."""
        text = self.text()
        if len(text) >= 3:
            # This will be handled by the parent dialog/window
            self.suggestion_requested.emit(self.field_type, text)
    
    def show_suggestion(self, suggestion: str):
        """Show a suggestion in the completer dropdown."""
        if not suggestion:
            return
        
        # Clean up suggestion
        suggestion = suggestion.strip()
        
        # Show in completer
        model = QStringListModel([suggestion])
        self._completer.setModel(model)
        self._completer.complete()
    
    def _insert_completion(self, completion: str):
        """Insert the selected completion."""
        current = self.text()
        # Append the suggestion
        self.setText(current + " " + completion)
    
    def set_context(self, context: Dict[str, Any]):
        """Update context for suggestions."""
        self.context = context


class AutocompleteTextEdit(QTextEdit):
    """Text edit with AI-powered autocomplete suggestions."""
    
    suggestion_requested = Signal(str, str)  # field_type, current_text
    
    def __init__(
        self,
        field_type: str = "description",
        parent=None,
        context: Optional[Dict[str, Any]] = None,
        debounce_ms: int = 1200
    ):
        super().__init__(parent)
        self.field_type = field_type
        self.context = context or {}
        self._debounce_ms = debounce_ms
        self._suggestion_timer = QTimer()
        self._suggestion_timer.setSingleShot(True)
        self._suggestion_timer.timeout.connect(self._request_suggestion)
        self._last_text = ""
        self._showing_suggestion = False
        
        # Connect text changes
        self.textChanged.connect(self._on_text_changed)
    
    def _on_text_changed(self):
        """Handle text changes with debouncing."""
        # Check if autocomplete is enabled
        if not get_preferences().autocomplete_enabled:
            return
        
        text = self.toPlainText()
        
        # Only trigger if text is growing
        if len(text) >= 10 and len(text) > len(self._last_text):
            self._suggestion_timer.start(self._debounce_ms)
        else:
            self._suggestion_timer.stop()
        
        self._last_text = text
    
    def _request_suggestion(self):
        """Request AI suggestion for current text."""
        text = self.toPlainText()
        
        # Get last sentence or paragraph for context
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor)
        context_text = cursor.selectedText()
        
        if not context_text:
            context_text = text[-200:] if len(text) > 200 else text
        
        if len(context_text) >= 10:
            self.suggestion_requested.emit(self.field_type, context_text)
    
    def show_suggestion(self, suggestion: str):
        """Show suggestion as grayed-out preview text."""
        if not suggestion or self._showing_suggestion:
            return
        
        # Store current state
        cursor = self.textCursor()
        current_pos = cursor.position()
        
        # Insert suggestion in gray
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Insert with formatting
        fmt = cursor.charFormat()
        original_color = fmt.foreground()
        
        # Add suggestion in gray
        from PySide6.QtGui import QColor
        fmt.setForeground(QColor(128, 128, 128))
        cursor.insertText(" " + suggestion, fmt)
        
        # Reset format
        fmt.setForeground(original_color)
        self.setCurrentCharFormat(fmt)
        
        # Select the suggestion so user can delete it easily
        cursor.setPosition(current_pos)
        self.setTextCursor(cursor)
        
        self._showing_suggestion = True
        
        # Clear flag after a delay
        QTimer.singleShot(3000, lambda: setattr(self, '_showing_suggestion', False))
    
    def set_context(self, context: Dict[str, Any]):
        """Update context for suggestions."""
        self.context = context


class AutocompleteManager:
    """Manages autocomplete requests for multiple fields."""
    
    def __init__(self):
        from nico.ai.model_manager import get_model_manager
        self.model_manager = get_model_manager()
        self._pending_requests = {}
    
    async def get_suggestion(
        self,
        field_type: str,
        current_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Get AI suggestion for a field."""
        try:
            suggestion = await self.model_manager.suggest_autocomplete(
                field_type,
                current_text,
                context
            )
            return suggestion
        except Exception as e:
            print(f"Autocomplete error: {e}")
            return None
    
    def connect_field(self, field, context: Optional[Dict[str, Any]] = None):
        """Connect a field to autocomplete."""
        if isinstance(field, (AutocompleteLineEdit, AutocompleteTextEdit)):
            field.suggestion_requested.connect(
                lambda field_type, text: self._handle_request(field, field_type, text, context)
            )
    
    def _handle_request(
        self,
        field,
        field_type: str,
        current_text: str,
        context: Optional[Dict[str, Any]]
    ):
        """Handle autocomplete request asynchronously."""
        # Use QTimer to run async task without blocking UI
        from PySide6.QtCore import QTimer
        
        def run_async():
            import asyncio
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run the async function
                suggestion = loop.run_until_complete(
                    self.get_suggestion(field_type, current_text, context)
                )
                
                # Show suggestion in UI thread
                if suggestion:
                    field.show_suggestion(suggestion)
                    
            except Exception as e:
                print(f"Autocomplete error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                loop.close()
        
        # Run in separate thread to avoid blocking UI
        from threading import Thread
        thread = Thread(target=run_async, daemon=True)
        thread.start()
