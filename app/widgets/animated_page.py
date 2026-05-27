"""AnimatedPage — base class for stacked-widget pages with fade+slide-up on show."""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QPoint, pyqtProperty,
)


class AnimatedPage(QWidget):
    """Mixin-style base. Override `build_ui()` in subclasses."""

    def __init__(self, parent=None, *, slide_px: int = 12, duration_ms: int = 320):
        super().__init__(parent)
        self._slide_px = slide_px
        self._duration = duration_ms
        self._opacity_fx = QGraphicsOpacityEffect(self)
        self._opacity_fx.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_fx)
        self._content_offset = 0  # animated via pyqtProperty
        self.build_ui()

    # subclasses override
    def build_ui(self) -> None:
        pass

    # Animated transform: shifts children up via paintevent offset.
    # Simpler approach: use move() on self for slide-up while opacity fades in.
    def play_enter(self) -> None:
        group = QParallelAnimationGroup(self)

        fade = QPropertyAnimation(self._opacity_fx, b"opacity")
        fade.setDuration(self._duration)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        group.addAnimation(fade)

        slide = QPropertyAnimation(self, b"pos")
        end = self.pos()
        start = QPoint(end.x(), end.y() + self._slide_px)
        slide.setDuration(self._duration)
        slide.setStartValue(start)
        slide.setEndValue(end)
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)
        group.addAnimation(slide)

        # Pre-set initial state then start
        self._opacity_fx.setOpacity(0.0)
        self.move(start)
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)
