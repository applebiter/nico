"""User preferences and settings."""
from typing import Literal, Dict, Any
from pathlib import Path
import json

ThemeMode = Literal["dark", "light"]


class Preferences:
    """Application preferences."""
    
    # Default values
    DEFAULT_THEME: ThemeMode = "dark"
    DEFAULT_FONT_SCALE = 100  # percentage
    DEFAULT_EDITOR_FONT = "Georgia"
    DEFAULT_EDITOR_FONT_SIZE = 14
    DEFAULT_AI_MODULES = {
        "quick_actions": True,
        "chat": True,
        "context_info": True,
        "model_selector": True,
    }
    
    def __init__(self) -> None:
        self.theme: ThemeMode = self.DEFAULT_THEME
        self.font_scale: int = self.DEFAULT_FONT_SCALE
        self.editor_font: str = self.DEFAULT_EDITOR_FONT
        self.editor_font_size: int = self.DEFAULT_EDITOR_FONT_SIZE
        self.ai_modules: Dict[str, bool] = self.DEFAULT_AI_MODULES.copy()
        self.llm_team: Dict[str, Any] = {"members": [], "primary_id": None}
        self._config_file = Path.home() / ".nico" / "preferences.json"
        
    def load(self) -> None:
        """Load preferences from disk."""
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r') as f:
                    data = json.load(f)
                    self.theme = data.get("theme", self.DEFAULT_THEME)
                    self.font_scale = data.get("font_scale", self.DEFAULT_FONT_SCALE)
                    self.editor_font = data.get("editor_font", self.DEFAULT_EDITOR_FONT)
                    self.editor_font_size = data.get("editor_font_size", self.DEFAULT_EDITOR_FONT_SIZE)
                    self.ai_modules = data.get("ai_modules", self.DEFAULT_AI_MODULES.copy())
                    self.llm_team = data.get("llm_team", {"members": [], "primary_id": None})
            except Exception as e:
                print(f"Error loading preferences: {e}")
    
    def save(self) -> None:
        """Save preferences to disk."""
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, 'w') as f:
                json.dump({
                    "theme": self.theme,
                    "font_scale": self.font_scale,
                    "editor_font": self.editor_font,
                    "editor_font_size": self.editor_font_size,
                    "ai_modules": self.ai_modules,
                    "llm_team": self.llm_team,
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")


# Global preferences instance
_preferences: Preferences = None


def get_preferences() -> Preferences:
    """Get the global preferences instance."""
    global _preferences
    if _preferences is None:
        _preferences = Preferences()
        _preferences.load()
    return _preferences
