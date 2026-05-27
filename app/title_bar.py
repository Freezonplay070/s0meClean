"""Frameless window title bar — drag-to-move, min/max/close with hover glow."""
from __future__ import annotations

import qtawesome as qta
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QSize
from PyQt6.QtGui import QMouseEvent


class _WinButton(QPushButton):
    def __init__(self, icon_name: str, hover_color: str, parent=None):
        super().__init__(parent)
        self._icon = icon_name
        self._hover = hover_color
        self.setFixedSize(46, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIcon(qta.icon(icon_name, color="#8A93A6"))
        self.setIconSize(QSize(14, 14))
        self.setStyleSheet(self._qss("#8A93A6", "transparent"))

    def _qss(self, fg: str, bg: str) -> str:
        return f"""
        QPushButton {{ background: {bg}; border: 0; }}
        """

    def enterEvent(self, e):
        bg = self._hover
        self.setIcon(qta.icon(self._icon, color="#FFFFFF"))
        self.setStyleSheet(self._qss("#FFFFFF", bg))
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.setIcon(qta.icon(self._icon, color="#8A93A6"))
        self.setStyleSheet(self._qss("#8A93A6", "transparent"))
        super().leaveEvent(e)


class TitleBar(QWidget):
    minimizeClicked = pyqtSignal()
    maximizeToggled = pyqtSignal()
    closeClicked = pyqtSignal()

    def __init__(self, parent=None, *, title: str = "s0meClean"):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(36)

        self._drag_pos: QPoint | None = None
        self._maximized = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 0, 0)
        layout.setSpacing(8)

        # App label (left)
        self._title = QLabel(title, self)
        self._title.setObjectName("titleBarLabel")
        layout.addWidget(self._title)
        layout.addStretch(1)

        # Window controls
        self._btn_min = _WinButton("fa5s.window-minimize", "#23293A", self)
        self._btn_max = _WinButton("fa5s.window-maximize", "#23293A", self)
        self._btn_close = _WinButton("fa5s.times", "#FF0055", self)
        for b in (self._btn_min, self._btn_max, self._btn_close):
            layout.addWidget(b)

        self._btn_min.clicked.connect(self.minimizeClicked.emit)
        self._btn_max.clicked.connect(self._toggle_max)
        self._btn_close.clicked.connect(self.closeClicked.emit)

    # ----------------- maximize / restore icon swap
    def _toggle_max(self):
        self._maximized = not self._maximized
        icon = "fa5s.window-restore" if self._maximized else "fa5s.window-maximize"
        self._btn_max._icon = icon
        self._btn_max.setIcon(qta.icon(icon, color="#8A93A6"))
        self.maximizeToggled.emit()

    # ----------------- drag to move (host window)
    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        if self._drag_pos is not None and e.buttons() & Qt.MouseButton.LeftButton:
            self.window().move(e.globalPosition().toPoint() - self._drag_pos)
            e.accept()

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self._drag_pos = None

    def mouseDoubleClickEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            self._toggle_max()
