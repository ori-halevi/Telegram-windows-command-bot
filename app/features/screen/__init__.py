from .handlers import match_text, register

# Re-export service helpers used by other features (switcher, start_help)
from .service import record_screen, take_screenshot

__all__ = ["match_text", "register", "record_screen", "take_screenshot"]
