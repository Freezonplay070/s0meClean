"""Windows 11 Mica / Acrylic backdrop via DWM API.

Usage:
    apply_mica(window.winId().__int__())  # after window is shown
"""
from __future__ import annotations

import sys
import ctypes
from ctypes import wintypes

# DWM attribute constants
_DWMWA_USE_IMMERSIVE_DARK_MODE = 20
_DWMWA_SYSTEMBACKDROP_TYPE = 38
_DWMWA_MICA_EFFECT = 1029  # legacy (Win11 22H2-)

# Backdrop types
_DWMSBT_AUTO = 0
_DWMSBT_NONE = 1
_DWMSBT_MAINWINDOW = 2          # Mica
_DWMSBT_TRANSIENTWINDOW = 3     # Acrylic
_DWMSBT_TABBEDWINDOW = 4        # Mica Alt


def _win_build() -> int:
    if sys.platform != "win32":
        return 0
    return sys.getwindowsversion().build


def _set_attr(hwnd: int, attr: int, value: int) -> bool:
    try:
        dwm = ctypes.windll.dwmapi
        v = ctypes.c_int(value)
        result = dwm.DwmSetWindowAttribute(
            wintypes.HWND(hwnd), wintypes.DWORD(attr),
            ctypes.byref(v), ctypes.sizeof(v),
        )
        return result == 0
    except Exception:
        return False


def enable_dark_titlebar(hwnd: int) -> None:
    _set_attr(hwnd, _DWMWA_USE_IMMERSIVE_DARK_MODE, 1)


def apply_mica(hwnd: int, *, dark: bool = True) -> bool:
    """Try Mica → Acrylic → fallback. Returns True if any backdrop applied."""
    if sys.platform != "win32" or not hwnd:
        return False
    build = _win_build()
    if dark:
        enable_dark_titlebar(hwnd)
    # Win11 22H2+ supports DWMWA_SYSTEMBACKDROP_TYPE
    if build >= 22621:
        if _set_attr(hwnd, _DWMWA_SYSTEMBACKDROP_TYPE, _DWMSBT_MAINWINDOW):
            return True
    # Older Win11 builds: legacy mica attribute
    if build >= 22000:
        if _set_attr(hwnd, _DWMWA_MICA_EFFECT, 1):
            return True
    return False


def apply_acrylic(hwnd: int, *, dark: bool = True) -> bool:
    """Translucent acrylic backdrop (good for modals/popups)."""
    if sys.platform != "win32" or not hwnd:
        return False
    if dark:
        enable_dark_titlebar(hwnd)
    if _win_build() >= 22621:
        return _set_attr(hwnd, _DWMWA_SYSTEMBACKDROP_TYPE, _DWMSBT_TRANSIENTWINDOW)
    return False
