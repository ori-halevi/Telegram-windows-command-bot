from .handlers import match_text, register

# Re-export send_combo for the macros feature.
from .service import send_combo, send_combos, type_text

__all__ = ["match_text", "register", "send_combo", "send_combos", "type_text"]
