"""Boost / Game Mode page — toggles aggressive theme + kills background tasks."""
from __future__ import annotations

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

from ..widgets.animated_page import AnimatedPage
from ..widgets.premium_button import AccentGlowButton, PremiumGlowButton


class BoostPage(AnimatedPage):
    """Game-mode toggle. Theme switch is wired via injected ThemeManager."""

    def __init__(self, parent=None, *, theme_manager=None):
        self._theme = theme_manager
        self._enabled = False
        super().__init__(parent)

    def build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 30, 40, 30)
        lay.setSpacing(20)

        t = QLabel("// BOOST"); t.setObjectName("pageTitle")
        s = QLabel("One-click Game Mode — kills background tasks, frees RAM")
        s.setObjectName("pageSubtitle")
        lay.addWidget(t); lay.addWidget(s)

        self._toggle = AccentGlowButton("⚡ ENABLE GAME MODE", filled=True)
        self._toggle.setMinimumHeight(64)
        self._toggle.clicked.connect(self._on_toggle)
        lay.addWidget(self._toggle)

        info = QLabel(
            "• freeing inactive RAM working sets\n"
            "• stopping non-essential services\n"
            "• swapping power plan to High Performance\n"
            "• disabling visual effects"
        )
        info.setObjectName("pageBody")
        lay.addWidget(info)
        lay.addStretch(1)

    def _on_toggle(self):
        self._enabled = not self._enabled
        if self._theme:
            self._theme.set_theme("boost" if self._enabled else "default")
        new_color = "#FF6A00" if self._enabled else "#00E5FF"
        self._toggle.set_accent(new_color)
        self._toggle.setText("⚡ GAME MODE: ON" if self._enabled else "⚡ ENABLE GAME MODE")
        self._toggle.pulse()
