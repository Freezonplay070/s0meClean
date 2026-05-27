"""Color palette + QSS variable substitution.

QSS not натівно not support variables, so we render templates ourselves.
Allows hot-swapping themes (e.g. Game Mode toggle → red/orange palette).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path

QSS_DIR = Path(__file__).parent / "qss"


@dataclass(frozen=True)
class Palette:
    """Color tokens. Use names, never hex literals, inside QSS templates."""
    bg: str = "#0B0E14"
    bg_elev: str = "#11151E"
    bg_card: str = "#161B26"
    bg_hover: str = "#1A1F2C"
    border: str = "#23293A"
    text: str = "#E6EAF2"
    text_dim: str = "#8A93A6"
    text_muted: str = "#5B6273"
    accent: str = "#00E5FF"          # neon cyan
    accent_dim: str = "#0099AA"
    accent_2: str = "#FF0055"        # neon magenta
    accent_2_dim: str = "#AA0033"
    ok: str = "#36E2A0"
    warn: str = "#FFB547"
    danger: str = "#FF4D5E"


# Pre-built themes
THEMES = {
    "default": Palette(),
    # Game Mode — agressive red/orange swap
    "boost": Palette(
        accent="#FF6A00",
        accent_dim="#B34A00",
        accent_2="#FF1744",
        accent_2_dim="#B30030",
        bg_card="#1C1410",
        bg_hover="#241910",
        border="#3A2418",
    ),
}


class ThemeManager:
    """Loads QSS files, substitutes color tokens, applies to QApplication."""

    def __init__(self, app, palette: Palette | None = None):
        self._app = app
        self._palette: Palette = palette or THEMES["default"]

    @property
    def palette(self) -> Palette:
        return self._palette

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        self.apply()

    def set_theme(self, name: str) -> None:
        if name not in THEMES:
            raise KeyError(f"Unknown theme: {name}")
        self.set_palette(THEMES[name])

    def apply(self) -> None:
        """Concat all QSS files in qss/ and inject palette."""
        qss_parts: list[str] = []
        for f in sorted(QSS_DIR.glob("*.qss")):
            qss_parts.append(f.read_text(encoding="utf-8"))
        raw = "\n".join(qss_parts)
        rendered = self._substitute(raw)
        self._app.setStyleSheet(rendered)

    def _substitute(self, qss: str) -> str:
        for key, value in asdict(self._palette).items():
            qss = qss.replace(f"@{key}", value)
        return qss
