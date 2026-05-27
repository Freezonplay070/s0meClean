"""Settings page — includes GitHub updater UI panel."""
from __future__ import annotations

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

from ..widgets.animated_page import AnimatedPage
from ..widgets.premium_button import PremiumGlowButton, AccentGlowButton
from ..core.github_updater import GithubUpdater, UpdateInfo
from .. import __version__, __github_repo__


class SettingsPage(AnimatedPage):
    def __init__(self, parent=None, *, theme_manager=None):
        self._theme = theme_manager
        self._updater = GithubUpdater(__github_repo__, __version__)
        self._latest: UpdateInfo | None = None
        super().__init__(parent)

    def build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 30, 40, 30)
        lay.setSpacing(18)

        t = QLabel("// SETTINGS"); t.setObjectName("pageTitle")
        s = QLabel("Theme · updates · about")
        s.setObjectName("pageSubtitle")
        lay.addWidget(t); lay.addWidget(s)

        # Updates section
        self._update_title = QLabel(f"Current version: v{__version__}")
        self._update_title.setObjectName("pageBody")
        lay.addWidget(self._update_title)

        self._update_status = QLabel("Натисни 'Check for updates'")
        self._update_status.setObjectName("pageBody")
        lay.addWidget(self._update_status)

        self._progress = QProgressBar(self)
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFixedHeight(8)
        self._progress.setTextVisible(False)
        self._progress.setObjectName("updateProgress")
        lay.addWidget(self._progress)

        row = QHBoxLayout(); row.setSpacing(12)
        self._btn_check = PremiumGlowButton("Check for updates")
        self._btn_download = AccentGlowButton("Download & Install", filled=True)
        self._btn_download.setEnabled(False)
        row.addWidget(self._btn_check)
        row.addWidget(self._btn_download)
        row.addStretch(1)
        lay.addLayout(row)

        self._btn_check.clicked.connect(self._on_check)
        self._btn_download.clicked.connect(self._on_download)

        # signals from updater
        self._updater.checkFinished.connect(self._on_check_finished)
        self._updater.downloadProgress.connect(self._on_progress)
        self._updater.downloadFinished.connect(self._on_download_finished)
        self._updater.error.connect(self._on_error)

        lay.addStretch(1)

    # -------- handlers
    def _on_check(self):
        self._update_status.setText("Перевіряю GitHub…")
        self._updater.check_async()

    def _on_check_finished(self, info: UpdateInfo, has_update: bool):
        self._latest = info
        if has_update:
            self._update_status.setText(
                f"Доступна нова версія: v{info.version}  ({info.size_human})"
            )
            self._btn_download.setEnabled(True)
        else:
            self._update_status.setText("У вас остання версія ✓")

    def _on_download(self):
        if not self._latest:
            return
        self._update_status.setText(f"Завантажую v{self._latest.version}…")
        self._updater.download_async(self._latest)

    def _on_progress(self, percent: int, downloaded: int, total: int):
        self._progress.setValue(percent)
        mb = downloaded / 1024 / 1024
        total_mb = total / 1024 / 1024 if total else 0
        self._update_status.setText(
            f"Завантаження… {percent}%  ({mb:.1f} / {total_mb:.1f} MB)"
        )

    def _on_download_finished(self, file_path: str):
        self._update_status.setText(
            f"Готово. Файл збережено: {file_path}\nЗапусти updater.exe для встановлення."
        )

    def _on_error(self, message: str):
        self._update_status.setText(f"⚠ {message}")
