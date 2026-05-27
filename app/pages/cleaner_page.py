"""Cleaner page — placeholder with premium buttons demonstrating UX."""
from __future__ import annotations

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

from ..widgets.animated_page import AnimatedPage
from ..widgets.premium_button import PremiumGlowButton, DangerGlowButton, AccentGlowButton


class CleanerPage(AnimatedPage):
    def build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 30, 40, 30)
        lay.setSpacing(18)

        t = QLabel("// CLEANER"); t.setObjectName("pageTitle")
        s = QLabel("Видалення сміття, фантомних записів та сторонніх кешів")
        s.setObjectName("pageSubtitle")
        lay.addWidget(t); lay.addWidget(s)

        row = QHBoxLayout(); row.setSpacing(14)
        row.addWidget(AccentGlowButton("⚡ QUICK AUDIT"))
        row.addWidget(PremiumGlowButton("Junk & Temp"))
        row.addWidget(PremiumGlowButton("Phantom Programs", accent="#FF0055"))
        row.addWidget(DangerGlowButton("Force Clean All"))
        row.addStretch(1)
        lay.addLayout(row)

        lay.addStretch(1)
