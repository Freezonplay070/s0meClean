"""MainWindow — frameless host. Wires up TitleBar + Sidebar + StackedContent."""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QFrame,
)
from PyQt6.QtCore import Qt

from .title_bar import TitleBar
from .sidebar import Sidebar, NavItem
from .core.win_effects import apply_mica
from .pages.cleaner_page import CleanerPage
from .pages.boost_page import BoostPage
from .pages.monitor_page import MonitorPage
from .pages.settings_page import SettingsPage


NAV_ITEMS = [
    NavItem("cleaner",  "CLEANER",  "fa5s.broom"),
    NavItem("boost",    "BOOST",    "fa5s.bolt"),
    NavItem("monitor",  "MONITOR",  "fa5s.chart-line"),
    NavItem("terminal", "TERMINAL", "fa5s.terminal"),
    NavItem("drivers",  "DRIVERS",  "fa5s.microchip"),
    NavItem("settings", "SETTINGS", "fa5s.cog"),
]


class MainWindow(QMainWindow):
    def __init__(self, theme_manager):
        super().__init__()
        self._theme = theme_manager

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setMinimumSize(1180, 740)
        self.resize(1320, 820)
        self.setWindowTitle("s0meClean")

        self._build_ui()

    # ----------------------------------------------------------- UI
    def _build_ui(self) -> None:
        central = QWidget(self)
        central.setObjectName("rootContainer")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ----- title bar
        self._title = TitleBar(self, title="s0meClean v2.0.0")
        self._title.minimizeClicked.connect(self.showMinimized)
        self._title.maximizeToggled.connect(self._toggle_max)
        self._title.closeClicked.connect(self.close)
        root.addWidget(self._title)

        # ----- body: sidebar + content
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        root.addLayout(body, 1)

        self._sidebar = Sidebar(NAV_ITEMS, self)
        self._sidebar.tabChanged.connect(self._on_tab_changed)
        body.addWidget(self._sidebar)

        # vertical accent divider
        divider = QFrame(self)
        divider.setObjectName("sidebarDivider")
        divider.setFixedWidth(1)
        body.addWidget(divider)

        # content stack
        self._stack = QStackedWidget(self)
        self._stack.setObjectName("contentStack")
        body.addWidget(self._stack, 1)

        # pages
        self._pages = {
            "cleaner":  CleanerPage(self),
            "boost":    BoostPage(self, theme_manager=self._theme),
            "monitor":  MonitorPage(self),
            "terminal": self._placeholder("AI TERMINAL", "Розумний термінал з парсингом команд"),
            "drivers":  self._placeholder("DRIVERS",     "Сканер та оновлення драйверів"),
            "settings": SettingsPage(self, theme_manager=self._theme),
        }
        for page in self._pages.values():
            self._stack.addWidget(page)

        self._sidebar.set_active("cleaner", animate=False)

    def _placeholder(self, title: str, sub: str):
        """Quick stub for pages not yet implemented."""
        from PyQt6.QtWidgets import QLabel
        w = QWidget(self)
        lay = QVBoxLayout(w); lay.setContentsMargins(40, 40, 40, 40)
        t = QLabel(f"// {title}");  t.setObjectName("pageTitle")
        s = QLabel(sub);            s.setObjectName("pageSubtitle")
        lay.addWidget(t); lay.addWidget(s); lay.addStretch(1)
        return w

    # ----------------------------------------------------------- events
    def showEvent(self, e):
        super().showEvent(e)
        # apply Mica AFTER first show so HWND exists
        try:
            apply_mica(int(self.winId()))
        except Exception:
            pass

    def _toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _on_tab_changed(self, key: str):
        page = self._pages.get(key)
        if not page:
            return
        self._stack.setCurrentWidget(page)
        # play enter animation if page supports it
        if hasattr(page, "play_enter"):
            page.play_enter()
