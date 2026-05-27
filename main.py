"""s0meClean entry point.

Run:
    python main.py
"""
from __future__ import annotations

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from app.main_window import MainWindow
from app.styles.theme import ThemeManager


def main() -> int:
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True) \
        if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling") else None

    app = QApplication(sys.argv)
    app.setApplicationName("s0meClean")
    app.setApplicationVersion("2.0.0")

    theme = ThemeManager(app)
    theme.apply()

    window = MainWindow(theme_manager=theme)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
