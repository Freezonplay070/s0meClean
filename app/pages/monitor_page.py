"""Monitor — live CPU/RAM cards via psutil + QTimer."""
from __future__ import annotations

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import QTimer

import psutil

from ..widgets.animated_page import AnimatedPage


class _StatCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        lay = QVBoxLayout(self); lay.setContentsMargins(20, 16, 20, 16)
        self._title = QLabel(title); self._title.setObjectName("statTitle")
        self._value = QLabel("—"); self._value.setObjectName("statValue")
        lay.addWidget(self._title); lay.addWidget(self._value)

    def set_value(self, v: str):
        self._value.setText(v)


class MonitorPage(AnimatedPage):
    def build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 30, 40, 30)
        lay.setSpacing(20)

        t = QLabel("// MONITOR"); t.setObjectName("pageTitle")
        s = QLabel("Live system stats")
        s.setObjectName("pageSubtitle")
        lay.addWidget(t); lay.addWidget(s)

        row = QHBoxLayout(); row.setSpacing(16)
        self._cpu = _StatCard("CPU")
        self._ram = _StatCard("RAM")
        self._disk = _StatCard("DISK C:")
        for c in (self._cpu, self._ram, self._disk):
            row.addWidget(c, 1)
        lay.addLayout(row); lay.addStretch(1)

        self._timer = QTimer(self)
        self._timer.setInterval(1500)
        self._timer.timeout.connect(self._tick)
        self._timer.start()
        self._tick()

    def _tick(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        try:
            disk = psutil.disk_usage("C:\\").percent
        except Exception:
            disk = 0
        self._cpu.set_value(f"{cpu:.0f}%")
        self._ram.set_value(f"{ram:.0f}%")
        self._disk.set_value(f"{disk:.0f}%")
