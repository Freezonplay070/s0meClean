"""Premium glow buttons with animated neon shadow + color transitions."""
from __future__ import annotations

from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    pyqtProperty, Qt,
)
from PyQt6.QtGui import QColor


class PremiumGlowButton(QPushButton):
    """Neon-glow button with animated drop shadow on hover.

    Args:
        text:   button label
        accent: primary glow color (hex)
        ink:    text color (hex); auto-derived if None
        filled: True → solid filled style; False → outlined (default)
    """

    def __init__(
        self,
        text: str = "",
        parent=None,
        *,
        accent: str = "#00E5FF",
        ink: str | None = None,
        filled: bool = False,
        glow_radius: int = 28,
        animation_ms: int = 280,
    ):
        super().__init__(text, parent)
        self._accent = accent
        self._ink = ink or ("#0B0E14" if filled else accent)
        self._filled = filled
        self._glow_radius = glow_radius

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(200, 44)
        self.setStyleSheet(self._build_qss())

        # Neon glow shadow
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(0)
        self._shadow.setColor(QColor(accent))
        self._shadow.setOffset(0, 0)
        self.setGraphicsEffect(self._shadow)

        # Glow animation
        self._anim_glow = QPropertyAnimation(self._shadow, b"blurRadius", self)
        self._anim_glow.setDuration(animation_ms)
        self._anim_glow.setEasingCurve(QEasingCurve.Type.OutCubic)

    # ----------------------------------------------------------- styling
    def _build_qss(self) -> str:
        if self._filled:
            return f"""
            QPushButton {{
                background: {self._accent};
                color: {self._ink};
                border: 1px solid {self._accent};
                border-radius: 10px;
                padding: 0 24px;
                font-family: 'Inter', 'Segoe UI';
                font-weight: 700;
                font-size: 13px;
                letter-spacing: 1.2px;
            }}
            QPushButton:hover  {{ background: {self._accent}; }}
            QPushButton:pressed {{ padding-top: 2px; }}
            QPushButton:disabled {{
                background: #1A1F2C; color: #5B6273; border-color: #23293A;
            }}
            """
        # outlined
        return f"""
        QPushButton {{
            background: rgba(0,0,0,0);
            color: {self._accent};
            border: 1px solid {self._accent};
            border-radius: 10px;
            padding: 0 24px;
            font-family: 'Inter', 'Segoe UI';
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 1.2px;
        }}
        QPushButton:hover  {{
            background: {self._accent};
            color: #0B0E14;
        }}
        QPushButton:pressed {{ padding-top: 2px; }}
        QPushButton:disabled {{
            color: #5B6273; border-color: #23293A;
        }}
        """

    # ----------------------------------------------------------- hover anims
    def enterEvent(self, event):
        self._anim_glow.stop()
        self._anim_glow.setStartValue(self._shadow.blurRadius())
        self._anim_glow.setEndValue(self._glow_radius)
        self._anim_glow.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._anim_glow.stop()
        self._anim_glow.setStartValue(self._shadow.blurRadius())
        self._anim_glow.setEndValue(0)
        self._anim_glow.start()
        super().leaveEvent(event)

    # ----------------------------------------------------------- runtime API
    def set_accent(self, color: str) -> None:
        """Hot-swap accent color (used by Game Mode theme change)."""
        self._accent = color
        if not self._filled:
            self._ink = color
        self._shadow.setColor(QColor(color))
        self.setStyleSheet(self._build_qss())

    def pulse(self) -> None:
        """One-shot glow burst — call after critical events (e.g. boost enabled)."""
        anim = QParallelAnimationGroup(self)
        up = QPropertyAnimation(self._shadow, b"blurRadius")
        up.setDuration(180); up.setStartValue(0); up.setEndValue(60)
        up.setEasingCurve(QEasingCurve.Type.OutQuad)
        down = QPropertyAnimation(self._shadow, b"blurRadius")
        down.setDuration(420); down.setStartValue(60); down.setEndValue(0)
        down.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.addAnimation(up); anim.addAnimation(down)
        anim.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)


class DangerGlowButton(PremiumGlowButton):
    def __init__(self, text="", parent=None, **kw):
        kw.setdefault("accent", "#FF0055")
        super().__init__(text, parent, **kw)


class AccentGlowButton(PremiumGlowButton):
    def __init__(self, text="", parent=None, **kw):
        kw.setdefault("accent", "#00E5FF")
        kw.setdefault("filled", True)
        super().__init__(text, parent, **kw)
