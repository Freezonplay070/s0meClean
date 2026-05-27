"""Sidebar with animated gradient indicator that slides between active tabs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import qtawesome as qta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QSize, pyqtProperty,
)
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QBrush


@dataclass
class NavItem:
    key: str
    label: str
    icon: str  # qtawesome name e.g. "fa5s.broom"


class _NavButton(QPushButton):
    def __init__(self, item: NavItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("navButton")
        self.setText("    " + item.label)
        self.setIcon(qta.icon(item.icon, color="#8A93A6"))
        self.setIconSize(QSize(20, 20))
        self.setFixedHeight(48)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def setActive(self, active: bool) -> None:
        self.setChecked(active)
        color = "#00E5FF" if active else "#8A93A6"
        self.setIcon(qta.icon(self.item.icon, color=color))


class _Indicator(QWidget):
    """Vertical pill that slides next to the active button. Painted with gradient."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(4)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#00E5FF"))
        grad.setColorAt(1.0, QColor("#FF0055"))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(self.rect(), 2, 2)


class Sidebar(QWidget):
    """Navigation sidebar. Emits `tabChanged(key)` when active tab changes."""

    tabChanged = pyqtSignal(str)

    def __init__(self, items: list[NavItem], parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)

        self._buttons: dict[str, _NavButton] = {}
        self._active_key: str | None = None
        self._build(items)

        self._indicator = _Indicator(self)
        self._indicator.setFixedHeight(28)
        self._indicator.hide()
        self._anim = QPropertyAnimation(self._indicator, b"geometry", self)
        self._anim.setDuration(280)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        if items:
            self.set_active(items[0].key, animate=False)

    # ------------------------------------------------------------- layout
    def _build(self, items: list[NavItem]) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 22, 14, 14)
        root.setSpacing(4)

        # Brand
        brand = QLabel("s0meClean", self)
        brand.setObjectName("brandLabel")
        sub = QLabel("// SYSTEM OPTIMIZATION SUITE", self)
        sub.setObjectName("brandSub")
        root.addWidget(brand)
        root.addWidget(sub)
        root.addSpacing(18)

        # Section header
        sect = QLabel("NAVIGATION", self)
        sect.setObjectName("sectionHeader")
        root.addWidget(sect)
        root.addSpacing(6)

        # Nav buttons
        for item in items:
            btn = _NavButton(item, self)
            btn.clicked.connect(lambda _=False, k=item.key: self.set_active(k))
            self._buttons[item.key] = btn
            root.addWidget(btn)

        root.addStretch(1)

        # Bottom status / version
        ver = QLabel("v2.0.0", self)
        ver.setObjectName("versionLabel")
        root.addWidget(ver)

    # ------------------------------------------------------------- API
    def set_active(self, key: str, *, animate: bool = True) -> None:
        if key not in self._buttons or key == self._active_key:
            return
        for k, b in self._buttons.items():
            b.setActive(k == key)
        self._active_key = key
        self._move_indicator(key, animate=animate)
        self.tabChanged.emit(key)

    def _move_indicator(self, key: str, *, animate: bool) -> None:
        btn = self._buttons[key]
        # Map button rect to sidebar coords
        top_left = btn.mapTo(self, btn.rect().topLeft())
        x = 4  # near left edge
        y = top_left.y() + (btn.height() - 28) // 2
        target = QRect(x, y, 4, 28)
        self._indicator.show()
        if animate and not self._indicator.geometry().isEmpty():
            self._anim.stop()
            self._anim.setStartValue(self._indicator.geometry())
            self._anim.setEndValue(target)
            self._anim.start()
        else:
            self._indicator.setGeometry(target)

    # Recompute indicator pos on resize/show
    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._active_key:
            self._move_indicator(self._active_key, animate=False)
