"""github_updater.py — checks GitHub Releases API, downloads assets in background.

Signals (PyQt6) emitted from worker threads. UI thread connects and animates
the progress bar smoothly via QPropertyAnimation in the receiver.

Public API:
    GithubUpdater(repo, current_version).check_async()
    -> emits checkFinished(UpdateInfo, has_update: bool)
    GithubUpdater.download_async(info)
    -> emits downloadProgress(percent, bytes_done, total_bytes)
    -> emits downloadFinished(path)
    -> emits error(message) on any failure
"""
from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests
from packaging.version import Version, InvalidVersion
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QMutex, QMutexLocker


# ---------------------------------------------------------------- model
@dataclass
class UpdateInfo:
    version: str            # e.g. "2.1.0"
    tag: str                # GitHub tag, e.g. "v2.1.0"
    name: str               # release name
    notes: str              # release body (markdown)
    asset_url: str          # direct download URL
    asset_name: str         # filename
    size_bytes: int         # asset size

    @property
    def size_human(self) -> str:
        n = self.size_bytes
        for u in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.1f} {u}"
            n /= 1024
        return f"{n:.1f} TB"


# ---------------------------------------------------------------- workers
class _CheckWorker(QThread):
    finished_ = pyqtSignal(object, bool)    # UpdateInfo, has_update
    failed = pyqtSignal(str)

    def __init__(self, repo: str, current: str, asset_pattern: str):
        super().__init__()
        self._repo = repo
        self._current = current
        self._pattern = re.compile(asset_pattern, re.IGNORECASE)

    def run(self):
        try:
            url = f"https://api.github.com/repos/{self._repo}/releases/latest"
            r = requests.get(url, timeout=15, headers={"Accept": "application/vnd.github+json"})
            r.raise_for_status()
            data = r.json()
            tag = (data.get("tag_name") or "").lstrip("v")
            assets = data.get("assets") or []
            asset = next((a for a in assets if self._pattern.search(a["name"])), None)
            if not asset:
                self.failed.emit("Підходящого .exe assetу у релізі не знайдено")
                return
            info = UpdateInfo(
                version=tag,
                tag=data.get("tag_name") or tag,
                name=data.get("name") or tag,
                notes=data.get("body") or "",
                asset_url=asset["browser_download_url"],
                asset_name=asset["name"],
                size_bytes=int(asset.get("size") or 0),
            )
            self.finished_.emit(info, self._is_newer(tag))
        except requests.RequestException as e:
            self.failed.emit(f"Network error: {e}")
        except Exception as e:
            self.failed.emit(f"Update check failed: {e}")

    def _is_newer(self, remote: str) -> bool:
        try:
            return Version(remote) > Version(self._current)
        except InvalidVersion:
            return remote != self._current


class _DownloadWorker(QThread):
    progress = pyqtSignal(int, int, int)   # percent, done, total
    finished_ = pyqtSignal(str)            # path
    failed = pyqtSignal(str)
    _cancel_mtx = QMutex()

    def __init__(self, info: UpdateInfo, dest_dir: Path):
        super().__init__()
        self._info = info
        self._dest_dir = dest_dir
        self._cancelled = False

    def cancel(self):
        with QMutexLocker(self._cancel_mtx):
            self._cancelled = True

    def run(self):
        try:
            self._dest_dir.mkdir(parents=True, exist_ok=True)
            dest = self._dest_dir / self._info.asset_name
            tmp = dest.with_suffix(dest.suffix + ".part")
            with requests.get(self._info.asset_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total = int(r.headers.get("Content-Length") or self._info.size_bytes or 0)
                done = 0
                last_pct = -1
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=64 * 1024):
                        with QMutexLocker(self._cancel_mtx):
                            if self._cancelled:
                                raise RuntimeError("Cancelled")
                        if not chunk:
                            continue
                        f.write(chunk)
                        done += len(chunk)
                        if total:
                            pct = int(done * 100 / total)
                            if pct != last_pct:
                                last_pct = pct
                                self.progress.emit(pct, done, total)
            os.replace(tmp, dest)
            self.finished_.emit(str(dest))
        except Exception as e:
            self.failed.emit(f"Download failed: {e}")


# ---------------------------------------------------------------- facade
class GithubUpdater(QObject):
    """Public facade. Hides worker threads behind clean signals."""

    checkFinished = pyqtSignal(object, bool)
    downloadProgress = pyqtSignal(int, int, int)
    downloadFinished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(
        self,
        repo: str,
        current_version: str,
        *,
        asset_pattern: str = r"\.exe$",
        download_dir: Optional[Path] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._repo = repo
        self._current = current_version
        self._asset_pattern = asset_pattern
        self._dl_dir = download_dir or Path(tempfile.gettempdir()) / "s0meclean_updates"
        self._check_worker: Optional[_CheckWorker] = None
        self._dl_worker: Optional[_DownloadWorker] = None

    # -------- check
    def check_async(self) -> None:
        if self._check_worker and self._check_worker.isRunning():
            return
        self._check_worker = _CheckWorker(self._repo, self._current, self._asset_pattern)
        self._check_worker.finished_.connect(self.checkFinished)
        self._check_worker.failed.connect(self.error)
        self._check_worker.start()

    # -------- download
    def download_async(self, info: UpdateInfo) -> None:
        if self._dl_worker and self._dl_worker.isRunning():
            return
        self._dl_worker = _DownloadWorker(info, self._dl_dir)
        self._dl_worker.progress.connect(self.downloadProgress)
        self._dl_worker.finished_.connect(self.downloadFinished)
        self._dl_worker.failed.connect(self.error)
        self._dl_worker.start()

    def cancel_download(self) -> None:
        if self._dl_worker and self._dl_worker.isRunning():
            self._dl_worker.cancel()
