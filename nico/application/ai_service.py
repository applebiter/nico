"""AI service for handling LLM interactions from the UI."""
import asyncio
from typing import Optional, Callable
from PySide6.QtCore import QObject, Signal, QThread

from nico.ai.manager import get_llm_team
from nico.ai.providers import LLMConfig


class AsyncLLMThread(QThread):
    """Thread for running async LLM operations."""
    
    response_ready = Signal(str)  # Emits the response text
    error = Signal(str)  # Emits error message
    
    def __init__(self, prompt: str, llm_id: Optional[str] = None):
        super().__init__()
        self.prompt = prompt
        self.llm_id = llm_id
    
    def run(self):
        """Run the LLM generation."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            team = get_llm_team()
            
            if self.llm_id:
                # Use specific LLM
                provider = team.get_member(self.llm_id)
                if not provider:
                    self.error.emit(f"LLM {self.llm_id} not found")
                    return
                response = loop.run_until_complete(provider.generate(self.prompt))
            else:
                # Use fallback chain (primary first)
                response = loop.run_until_complete(
                    team.generate_with_fallback(self.prompt)
                )
            
            self.response_ready.emit(response)
            
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")


class AIService(QObject):
    """Service for managing AI interactions from the UI."""
    
    response_ready = Signal(str, str)  # (response_text, llm_id)
    error = Signal(str)
    generating = Signal(bool)  # True when generating, False when done
    
    def __init__(self):
        super().__init__()
        self.team = get_llm_team()
        self.current_thread: Optional[AsyncLLMThread] = None
    
    def generate(self, prompt: str, llm_id: Optional[str] = None):
        """Generate a response using the specified LLM or the primary one."""
        if self.current_thread and self.current_thread.isRunning():
            # Already generating
            return
        
        self.generating.emit(True)
        
        self.current_thread = AsyncLLMThread(prompt, llm_id)
        self.current_thread.response_ready.connect(
            lambda resp: self._on_response_ready(resp, llm_id or "primary")
        )
        self.current_thread.error.connect(self._on_error)
        self.current_thread.finished.connect(lambda: self.generating.emit(False))
        self.current_thread.start()
    
    def _on_response_ready(self, response: str, llm_id: str):
        """Handle response from LLM."""
        self.response_ready.emit(response, llm_id)
    
    def _on_error(self, error_msg: str):
        """Handle error from LLM."""
        self.error.emit(error_msg)
        self.generating.emit(False)
    
    def list_available_llms(self):
        """Get list of enabled LLM configurations."""
        members = self.team.list_members()
        return [m for m in members if m.enabled]
    
    def get_primary_llm(self) -> Optional[LLMConfig]:
        """Get the primary LLM configuration."""
        return self.team.get_primary_config()


# Global instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get the global AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
