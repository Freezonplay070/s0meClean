# -*- coding: utf-8 -*-
"""
s0meClean? — Cyberpunk Disk Cleaner & Windows Optimizer
PySide6 GUI  ·  v1.0.0  ·  MIT License  ·  solevoyq
"""

import ctypes, json, os, platform, shutil, subprocess, sys, threading, time, traceback
import urllib.request, zipfile, winreg, locale
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

VERSION = "1.0.0"
GITHUB_REPO = "Freezonplay070/s0meClean"
GITHUB_API  = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
UPDATE_URL  = f"https://github.com/{GITHUB_REPO}/releases/latest/download/s0meClean.zip"

# ─── PySide6 ───
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QStackedWidget, QPushButton, QLabel, QFrame,
    QScrollArea, QProgressBar, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QCheckBox, QLineEdit, QFileDialog, QMessageBox,
    QComboBox, QGraphicsOpacityEffect, QSplitter, QSizePolicy,
    QTextEdit, QDialog, QDialogButtonBox, QGroupBox, QSpacerItem,
)
from PySide6.QtCore import (
    Qt, QTimer, Signal, QThread, QPropertyAnimation, QEasingCurve,
    QUrl, QSize, QPoint, QRect, QParallelAnimationGroup,
    QSequentialAnimationGroup, Property,
)
from PySide6.QtGui import (
    QFont, QColor, QPalette, QPainter, QLinearGradient, QRadialGradient,
    QPen, QBrush, QIcon, QPixmap, QFontDatabase, QDesktopServices,
    QPainterPath, QConicalGradient,
)

# ═══════════════════════════════════════════════════
#  COLORS — Cyberpunk Neon Palette
# ═══════════════════════════════════════════════════
class C:
    BG       = "#0a0e1a"
    BG2      = "#0f1428"
    PANEL    = "#121a2e"
    PANEL2   = "#1a2340"
    PANEL3   = "#243052"
    BORDER   = "#2a3660"
    TEXT     = "#dce6fa"
    DIM      = "#8c9ec3"
    MUTED    = "#5f6e8c"
    CYAN     = "#00f0ff"
    CYAN_D   = "#00b8c4"
    PINK     = "#ff1e82"
    PINK_D   = "#cc0055"
    YELLOW   = "#ffdc32"
    GREEN    = "#32e682"
    ORANGE   = "#ffb43c"
    RED      = "#ff4664"
    PURPLE   = "#a855f7"


# ═══════════════════════════════════════════════════
#  i18n — RUSSIAN + ENGLISH
# ═══════════════════════════════════════════════════
LANG = "EN"

STRINGS = {
    # Header
    "subtitle":       {"EN": "// CYBER DISK UTILITIES",       "RU": "// КИБЕР ДИСКОВЫЕ УТИЛИТЫ"},
    "drive":          {"EN": "DRIVE",                         "RU": "ДИСК"},
    "total":          {"EN": "TOTAL",                         "RU": "ВСЕГО"},
    "used":           {"EN": "USED",                          "RU": "ЗАНЯТО"},
    "free":           {"EN": "FREE",                          "RU": "СВОБОДНО"},
    "admin_yes":      {"EN": "● ADMIN",                       "RU": "● АДМИН"},
    "admin_no":       {"EN": "● NO ADMIN",                    "RU": "● НЕТ ПРАВ"},
    # Sidebar tabs
    "tab_clean":      {"EN": "CLEANING",                      "RU": "ОЧИСТКА"},
    "tab_opt":        {"EN": "OPTIMIZE",                      "RU": "ОПТИМИЗАЦИЯ"},
    "tab_browser":    {"EN": "BROWSERS",                      "RU": "БРАУЗЕРЫ"},
    "tab_custom":     {"EN": "CUSTOM SCAN",                   "RU": "СВОЙ СКАН"},
    "tab_settings":   {"EN": "SETTINGS",                      "RU": "НАСТРОЙКИ"},
    "scan_actions":   {"EN": "// SCAN ACTIONS",               "RU": "// ДЕЙСТВИЯ"},
    "github_btn":     {"EN": "★  GITHUB",                     "RU": "★  GITHUB"},
    "check_updates":  {"EN": "↻  CHECK UPDATES",              "RU": "↻  ОБНОВЛЕНИЯ"},
    # Clean page
    "results":        {"EN": "// RESULTS",                    "RU": "// РЕЗУЛЬТАТЫ"},
    "analysis":       {"EN": "ANALYSIS // RECOMMENDATIONS",   "RU": "АНАЛИЗ // РЕКОМЕНДАЦИИ"},
    "start_hint":     {"EN": "Select a scan action from the sidebar to begin.",
                       "RU": "Выберите действие сканирования в боковой панели."},
    "activity":       {"EN": "ACTIVITY",                      "RU": "АКТИВНОСТЬ"},
    "nothing_sel":    {"EN": "Nothing selected",              "RU": "Ничего не выбрано"},
    "delete_sel":     {"EN": "🗑  DELETE SELECTED",            "RU": "🗑  УДАЛИТЬ ВЫБРАННОЕ"},
    "open_explorer":  {"EN": "📂  OPEN IN EXPLORER",          "RU": "📂  В ПРОВОДНИКЕ"},
    "select_all":     {"EN": "SELECT ALL (Ctrl+A)",           "RU": "ВЫБРАТЬ ВСЁ (Ctrl+A)"},
    "scanning":       {"EN": "Scanning...",                   "RU": "Сканирование..."},
    "col_size":       {"EN": "SIZE",                          "RU": "РАЗМЕР"},
    "col_path":       {"EN": "PATH",                          "RU": "ПУТЬ"},
    "col_type":       {"EN": "TYPE",                          "RU": "ТИП"},
    # Scan sidebar actions
    "quick_audit":    {"EN": "⚡ QUICK AUDIT",                "RU": "⚡ БЫСТРЫЙ АУДИТ"},
    "largest_folders": {"EN": "📁 Largest folders",           "RU": "📁 Крупные папки"},
    "phantom_progs":  {"EN": "👻 Phantom programs",           "RU": "👻 Фантомные программы"},
    "orphan_folders": {"EN": "🔗 Orphan folders",             "RU": "🔗 Сиротские папки"},
    "large_files":    {"EN": "📦 Large files (>500MB)",       "RU": "📦 Большие файлы (>500МБ)"},
    "installed_progs": {"EN": "💾 Installed programs",        "RU": "💾 Установленные программы"},
    "junk_temp":      {"EN": "🗑 Junk (Temp, caches)",        "RU": "🗑 Мусор (Temp, кэш)"},
    "recycle_bin":    {"EN": "♻ Recycle bin",                  "RU": "♻ Корзина"},
    "hiberfil":       {"EN": "💤 Hiberfil.sys",               "RU": "💤 Hiberfil.sys"},
    "open_opt_tab":   {"EN": "▶ Open Optimization tab",      "RU": "▶ Вкладка Оптимизации"},
    # Optimization page
    "opt_title":      {"EN": "// WINDOWS OPTIMIZATION",       "RU": "// ОПТИМИЗАЦИЯ WINDOWS"},
    "opt_desc":       {"EN": "Choose a level. Check the actions you want, then click APPLY.",
                       "RU": "Выберите уровень. Отметьте нужные действия и нажмите ПРИМЕНИТЬ."},
    "apply":          {"EN": "APPLY  ▶",                      "RU": "ПРИМЕНИТЬ  ▶"},
    "quick_actions":  {"EN": "QUICK ACTIONS",                 "RU": "БЫСТРЫЕ ДЕЙСТВИЯ"},
    # Opt presets
    "opt_light":      {"EN": "LIGHT",                         "RU": "ЛЁГКИЙ"},
    "opt_light_d":    {"EN": "Safe tweaks. Speed boost without breaking anything.",
                       "RU": "Безопасные настройки. Ускорение без риска."},
    "opt_medium":     {"EN": "MEDIUM",                        "RU": "СРЕДНИЙ"},
    "opt_medium_d":   {"EN": "Disables telemetry, ads, Cortana. Noticeable speedup.",
                       "RU": "Отключает телеметрию, рекламу, Cortana. Заметное ускорение."},
    "opt_heavy":      {"EN": "HEAVY",                         "RU": "ТЯЖЁЛЫЙ"},
    "opt_heavy_d":    {"EN": "Maximum performance. Disables services, effects. For power users!",
                       "RU": "Максимум производительности. Отключает службы и эффекты. Для опытных!"},
    # Opt actions
    "oa_temp":        {"EN": "Clear Temp + Prefetch",         "RU": "Очистить Temp + Prefetch"},
    "oa_menu":        {"EN": "Fast menu animation (delay=0)", "RU": "Быстрая анимация меню (delay=0)"},
    "oa_dns":         {"EN": "Flush DNS cache",               "RU": "Очистить DNS кэш"},
    "oa_fastboot":    {"EN": "Enable fast startup",           "RU": "Включить быстрый запуск"},
    "oa_telemetry":   {"EN": "Disable Windows telemetry",     "RU": "Отключить телеметрию Windows"},
    "oa_cortana":     {"EN": "Disable Cortana",               "RU": "Отключить Cortana"},
    "oa_ads":         {"EN": "Disable advertising ID",        "RU": "Отключить рекламный ID"},
    "oa_tips":        {"EN": "Disable Tips & Suggestions",    "RU": "Отключить советы и предложения"},
    "oa_eventlogs":   {"EN": "Clear Windows Event logs",      "RU": "Очистить логи событий Windows"},
    "oa_visual":      {"EN": "Visual effects → Performance",  "RU": "Эффекты → Производительность"},
    "oa_sysmain":     {"EN": "Disable SysMain (Superfetch)",  "RU": "Отключить SysMain (Superfetch)"},
    "oa_wsearch":     {"EN": "Disable Windows Search indexing","RU": "Отключить индексацию Windows Search"},
    "oa_hibernate":   {"EN": "Disable Hibernation (~6 GB)",   "RU": "Отключить гибернацию (~6 ГБ)"},
    "oa_power":       {"EN": "Power plan → High Performance", "RU": "Схема питания → Высокая производительность"},
    "oa_diagtrack":   {"EN": "Disable DiagTrack service",     "RU": "Отключить службу DiagTrack"},
    # Quick actions
    "qa_chkdsk":      {"EN": "chkdsk C: /scan",              "RU": "chkdsk C: /scan"},
    "qa_cleanmgr":    {"EN": "Disk Cleanup (cleanmgr)",       "RU": "Очистка диска (cleanmgr)"},
    "qa_defrag":      {"EN": "Defragment (dfrgui)",           "RU": "Дефрагментация (dfrgui)"},
    "qa_startup":     {"EN": "Task Manager → Startup",        "RU": "Диспетчер задач → Автозагрузка"},
    "qa_services":    {"EN": "Services (services.msc)",       "RU": "Службы (services.msc)"},
    # Browser page
    "browser_title":  {"EN": "// BROWSER CACHE CLEANUP",      "RU": "// ОЧИСТКА КЭША БРАУЗЕРОВ"},
    "browser_desc":   {"EN": "Scan and clean browser caches. Close browsers before cleaning for best results.",
                       "RU": "Сканирование и очистка кэша браузеров. Закройте браузеры для лучшего результата."},
    "scan_browsers":  {"EN": "🔍  SCAN BROWSER CACHES",       "RU": "🔍  СКАНИРОВАТЬ КЭШ БРАУЗЕРОВ"},
    "browser_hint":   {"EN": "Results will appear in the CLEANING tab after scan completes.",
                       "RU": "Результаты появятся на вкладке ОЧИСТКА после завершения скана."},
    # Custom scan page
    "custom_title":   {"EN": "// CUSTOM SCAN",                "RU": "// СВОЙ СКАН"},
    "custom_desc":    {"EN": "Pick a folder — shows largest subfolders and files inside.",
                       "RU": "Выберите папку — покажет крупнейшие подпапки и файлы внутри."},
    "path_label":     {"EN": "Path:",                         "RU": "Путь:"},
    "pick_folder":    {"EN": "PICK FOLDER",                   "RU": "ВЫБРАТЬ ПАПКУ"},
    "scan_go":        {"EN": "SCAN  ▶",                       "RU": "СКАН  ▶"},
    "custom_hint":    {"EN": "Results will appear in the CLEANING tab after scan.",
                       "RU": "Результаты появятся на вкладке ОЧИСТКА после скана."},
    # Settings page
    "settings_title": {"EN": "// SETTINGS",                   "RU": "// НАСТРОЙКИ"},
    "about":          {"EN": "ABOUT",                         "RU": "О ПРОГРАММЕ"},
    "about_text":     {"EN": "s0meClean? — Cyberpunk Disk Cleaner & Windows Optimizer.\n"
                             "Scan junk, phantom programs, orphan folders, browser caches.\n"
                             "Optimize Windows with 3 preset levels. Open source, MIT License.\n"
                             "by solevoyq",
                       "RU": "s0meClean? — Кибер-утилита очистки диска и оптимизации Windows.\n"
                             "Сканирование мусора, фантомных программ, сиротских папок, кэша.\n"
                             "Оптимизация Windows в 3 уровнях. Открытый код, лицензия MIT.\n"
                             "by solevoyq"},
    "access_key":     {"EN": "ACCESS KEY",                    "RU": "КЛЮЧ ДОСТУПА"},
    "activate":       {"EN": "ACTIVATE",                      "RU": "АКТИВИРОВАТЬ"},
    "key_none":       {"EN": "STATUS: Not activated",         "RU": "СТАТУС: Не активирован"},
    "key_active":     {"EN": "STATUS: ACTIVE  ·  Key:",       "RU": "СТАТУС: АКТИВЕН  ·  Ключ:"},
    "key_invalid":    {"EN": "STATUS: Invalid key format",    "RU": "СТАТУС: Неверный формат ключа"},
    "language":       {"EN": "LANGUAGE",                      "RU": "ЯЗЫК"},
    "lang_restart":   {"EN": "Language will change after restart.",
                       "RU": "Язык изменится после перезапуска."},
    # Status bar
    "status":         {"EN": "STATUS",                        "RU": "СТАТУС"},
    "ready":          {"EN": "Ready",                         "RU": "Готово"},
    "done":           {"EN": "Done",                          "RU": "Готово"},
    # Dialogs
    "confirm_del_t":  {"EN": "Confirm Deletion",              "RU": "Подтвердите удаление"},
    "confirm_del_m":  {"EN": "Delete {n} items? This cannot be undone for files.\n"
                             "Phantom entries will only be removed from registry.",
                       "RU": "Удалить {n} элементов? Это нельзя отменить для файлов.\n"
                             "Фантомные записи будут удалены только из реестра."},
    "result_title":   {"EN": "Result",                        "RU": "Результат"},
    "result_msg":     {"EN": "Success: {ok}\nErrors: {fail}\nFreed: {freed}",
                       "RU": "Успешно: {ok}\nОшибки: {fail}\nОсвобождено: {freed}"},
    "confirm_title":  {"EN": "Confirm",                       "RU": "Подтверждение"},
    "confirm_opt":    {"EN": "Apply {n} actions from '{title}'?",
                       "RU": "Применить {n} действий из '{title}'?"},
    "opt_done_t":     {"EN": "Done",                          "RU": "Готово"},
    "opt_done_m":     {"EN": "Applied: {ok}\nErrors: {fail}\n\nSome changes require a reboot.",
                       "RU": "Применено: {ok}\nОшибки: {fail}\n\nНекоторые изменения требуют перезагрузки."},
    "select_folder":  {"EN": "Select Folder",                 "RU": "Выберите папку"},
    # Update
    "checking_upd":   {"EN": "Checking for updates...",       "RU": "Проверка обновлений..."},
    "up_to_date":     {"EN": "Up to date",                    "RU": "Актуальная версия"},
    "upd_available_t": {"EN": "Update Available",             "RU": "Доступно обновление"},
    "upd_available_m": {"EN": "New version: v{ver}\nCurrent: v{cur}\n\nDownload and update?",
                        "RU": "Новая версия: v{ver}\nТекущая: v{cur}\n\nСкачать и обновить?"},
    "downloading":    {"EN": "Downloading update...",         "RU": "Скачивание обновления..."},
    "updated_t":      {"EN": "Updated",                       "RU": "Обновлено"},
    "updated_m":      {"EN": "Update installed. Restart the app.",
                       "RU": "Обновление установлено. Перезапустите приложение."},
    "upd_installed":  {"EN": "Update installed — restart required",
                       "RU": "Обновление установлено — требуется перезапуск"},
    "upd_failed":     {"EN": "Update failed",                 "RU": "Ошибка обновления"},
    # Scan results
    "items_found":    {"EN": "{n} items found",               "RU": "{n} элементов найдено"},
    "items_size":     {"EN": "{n} items  ·  {sz}",            "RU": "{n} элементов  ·  {sz}"},
    "sel_items":      {"EN": "Selected: {n} items · {sz}",    "RU": "Выбрано: {n} элементов · {sz}"},
    "scanning_t":     {"EN": "Scanning: {t}...",              "RU": "Сканирование: {t}..."},
    # Scan worker results (recommendations)
    "rec_junk":       {"EN": "Found {sz} of junk. Select all → Delete.",
                       "RU": "Найдено {sz} мусора. Выберите все → Удалить."},
    "rec_folders":    {"EN": "Found {n} large folders ({sz})",
                       "RU": "Найдено {n} крупных папок ({sz})"},
    "rec_files":      {"EN": "Found {n} files > 500 MB. .sys files must NOT be deleted.",
                       "RU": "Найдено {n} файлов > 500 МБ. Файлы .sys удалять НЕЛЬЗЯ."},
    "rec_no_phantom": {"EN": "No phantom programs found — registry is clean.",
                       "RU": "Фантомных программ нет — реестр чист."},
    "rec_phantom":    {"EN": "Found {n} phantom entries. Select all → Delete to clean registry.",
                       "RU": "Найдено {n} фантомных записей. Выберите все → Удалить для очистки."},
    "rec_orphans":    {"EN": "Found {n} orphan folders ({sz})",
                       "RU": "Найдено {n} сиротских папок ({sz})"},
    "rec_installed":  {"EN": "Found {n} installed programs (sorted by size)",
                       "RU": "Найдено {n} установленных программ (по размеру)"},
    "rec_recycle":    {"EN": "Recycle bin: {sz}",             "RU": "Корзина: {sz}"},
    "rec_hiber_off":  {"EN": "Hibernation is already disabled.",
                       "RU": "Гибернация уже отключена."},
    "rec_hiber_on":   {"EN": "hiberfil.sys = {sz}. Will run: powercfg /h off",
                       "RU": "hiberfil.sys = {sz}. Будет выполнено: powercfg /h off"},
    "rec_hiber_err":  {"EN": "Cannot read hiberfil.sys",     "RU": "Не удалось прочитать hiberfil.sys"},
    "rec_browser":    {"EN": "Browser caches: {sz}",         "RU": "Кэш браузеров: {sz}"},
    "rec_audit":      {"EN": "Quick audit complete. Select all (Ctrl+A) → Delete Selected.",
                       "RU": "Быстрый аудит завершён. Выберите все (Ctrl+A) → Удалить выбранное."},
    "rec_custom":     {"EN": "Custom scan: {n} items, {sz}",
                       "RU": "Свой скан: {n} элементов, {sz}"},
    "rec_path_err":   {"EN": "Path does not exist",          "RU": "Путь не существует"},
}


def T(key, **kw):
    """Translate string by key using current LANG."""
    s = STRINGS.get(key, {}).get(LANG, key)
    if kw:
        try:
            return s.format(**kw)
        except (KeyError, IndexError):
            return s
    return s


def _load_language():
    """Load language preference from config.json."""
    global LANG
    cfg = os.path.join(app_dir(), "config.json")
    try:
        if os.path.exists(cfg):
            with open(cfg, "r", encoding="utf-8") as f:
                data = json.load(f)
            lang = data.get("language", "EN").upper()
            if lang in ("RU", "EN"):
                LANG = lang
    except Exception:
        pass

# ═══════════════════════════════════════════════════
#  ADMIN CHECK
# ═══════════════════════════════════════════════════
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)

# ═══════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════
def format_size(b: int) -> str:
    if b >= 1024**3:
        return f"{b / 1024**3:.2f} GB"
    elif b >= 1024**2:
        return f"{b / 1024**2:.1f} MB"
    elif b >= 1024:
        return f"{b / 1024:.0f} KB"
    return f"{b} B"

def get_folder_size(path: str, max_files: int = 80000) -> int:
    """Get folder size with a file count cap to prevent hanging on huge dirs."""
    total = 0
    count = 0
    try:
        for dirpath, _dirnames, filenames in os.walk(path):
            for f in filenames:
                count += 1
                if count > max_files:
                    return total  # good enough estimate
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        pass
    return total

def app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════
#  DATA
# ═══════════════════════════════════════════════════
@dataclass
class ScanItem:
    path: str
    size: int
    details: str
    item_type: str       # folder, junk, phantom, file, recyclebin, hibernation, orphan, installed, browser, duplicate
    extra: str = ""

# ═══════════════════════════════════════════════════
#  SCAN WORKER THREAD
# ═══════════════════════════════════════════════════
class ScanWorker(QThread):
    progress = Signal(int, str)   # pct, status
    item_found = Signal(object)   # ScanItem
    log_msg = Signal(str)
    finished_scan = Signal(str)   # recommendation text

    def __init__(self, scan_type: str, drive: str = "C:", extra=None):
        super().__init__()
        self.scan_type = scan_type
        self.drive = drive
        self.extra = extra
        self._cancel = False

    def cancel(self):
        self._cancel = True

    # ── helpers ──
    def _log(self, msg):
        self.log_msg.emit(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def _emit(self, path, size, details, item_type, extra=""):
        self.item_found.emit(ScanItem(path, size, details, item_type, extra))

    # ── scan dispatcher ──
    def run(self):
        try:
            method = getattr(self, f"_scan_{self.scan_type}", None)
            if method:
                method()
            else:
                self.finished_scan.emit(f"Unknown scan: {self.scan_type}")
        except Exception as e:
            try:
                self._log(f"ERROR: {traceback.format_exc()}")
            except Exception:
                pass
            self.finished_scan.emit(f"Error: {e}")

    # ──────────── JUNK ────────────
    def _scan_junk(self):
        locs = [
            (os.environ.get("TEMP", ""), "User Temp"),
            (r"C:\Windows\Temp", "Windows Temp"),
            (r"C:\Windows\Prefetch", "Prefetch"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "Microsoft","Windows","INetCache"), "IE/Edge Cache"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "Google","Chrome","User Data","Default","Cache"), "Chrome Cache"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "Google","Chrome","User Data","Default","Code Cache"), "Chrome Code Cache"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "Microsoft","Edge","User Data","Default","Cache"), "Edge Cache"),
            (r"C:\Windows\SoftwareDistribution\Download", "Windows Update Cache"),
            (r"C:\Windows\Logs\CBS", "CBS Logs"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "CrashDumps"), "Crash Dumps"),
            (r"C:\Windows\Minidump", "Minidumps"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "D3DSCache"), "DirectX Shader Cache"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "NVIDIA","DXCache"), "NVIDIA DX Cache"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "NVIDIA","GLCache"), "NVIDIA GL Cache"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "Mozilla","Firefox","Profiles"), "Firefox Cache"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "Packages"), "UWP App Cache"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "Temp"), "Local Temp"),
        ]
        total_freed = 0
        for i, (p, name) in enumerate(locs):
            if self._cancel:
                break
            self.progress.emit(int((i / len(locs)) * 100), f"[{i+1}/{len(locs)}] {name}")
            self._log(f"Check: {name}")
            if p and os.path.isdir(p):
                sz = get_folder_size(p)
                if sz > 1024 * 1024:
                    self._emit(p, sz, name, "junk")
                    total_freed += sz
        self.finished_scan.emit(T("rec_junk", sz=format_size(total_freed)))

    # ──────────── LARGE FOLDERS ────────────
    SKIP_DIRS = {"windows", "$recycle.bin", "system volume information",
                 "$windows.~bt", "$windows.~ws", "recovery", "boot",
                 "documents and settings", "perflogs", "config.msi",
                 "$sysprepunattend", "msocache", "intel", "amd"}

    def _scan_largefolders(self):
        root = self.drive + "\\"
        try:
            entries = [os.path.join(root, d) for d in os.listdir(root)
                       if os.path.isdir(os.path.join(root, d))
                       and d.lower() not in self.SKIP_DIRS]
        except (PermissionError, OSError):
            entries = []
        total = max(1, len(entries))
        found = 0
        total_sz = 0
        for i, d in enumerate(entries):
            if self._cancel:
                break
            name = os.path.basename(d)
            self.progress.emit(int((i / total) * 90), f"[{i+1}/{total}] {name}")
            self._log(f"Measuring: {d}")
            try:
                sz = get_folder_size(d, max_files=50000)
            except Exception:
                continue
            if sz > 100 * 1024**2:
                self._emit(d, sz, "Folder", "folder")
                found += 1
                total_sz += sz
                # Dive into large folders
                if sz > 5 * 1024**3:
                    try:
                        for sub in os.listdir(d):
                            sp = os.path.join(d, sub)
                            if os.path.isdir(sp):
                                sz2 = get_folder_size(sp, max_files=30000)
                                if sz2 > 500 * 1024**2:
                                    self._emit(sp, sz2, "Subfolder", "folder")
                                    found += 1
                                    total_sz += sz2
                    except (PermissionError, OSError):
                        pass
        self.progress.emit(100, T("done"))
        self.finished_scan.emit(T("rec_folders", n=found, sz=format_size(total_sz)))

    # ──────────── LARGE FILES ────────────
    def _scan_largefiles(self):
        root = self.drive + "\\"
        found = []
        cnt = 0
        skip = {"windows", "$recycle.bin", "system volume information"}
        self._log(f"Scanning {root} for files > 500 MB...")
        for dirpath, _dirs, files in os.walk(root):
            if self._cancel:
                break
            # Skip system dirs at root level
            rel = os.path.relpath(dirpath, root).split(os.sep)[0].lower()
            if rel in skip:
                _dirs.clear()
                continue
            for f in files:
                cnt += 1
                if cnt % 5000 == 0:
                    self.progress.emit(min(95, cnt // 1000), f"Files: {cnt}")
                fp = os.path.join(dirpath, f)
                try:
                    sz = os.path.getsize(fp)
                    if sz > 500 * 1024**2:
                        found.append((fp, sz))
                except (OSError, PermissionError):
                    pass
        found.sort(key=lambda x: x[1], reverse=True)
        for fp, sz in found[:60]:
            ext = os.path.splitext(fp)[1].lower()
            note = {".sys": "SYSTEM (don't delete!)", ".iso": "ISO Image", ".mp4": "Video",
                    ".mkv": "Video", ".zip": "Archive", ".rar": "Archive", ".7z": "Archive",
                    ".pak": "Game resource", ".vhd": "VHD", ".log": "Log"}.get(ext, "File")
            self._emit(fp, sz, note, "file")
        self.progress.emit(100, f"Done. Files: {len(found[:60])}")
        self.finished_scan.emit(T("rec_files", n=len(found[:60])))

    # ──────────── PHANTOMS ────────────
    def _scan_phantoms(self):
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        entries = []
        for hkey, subpath in reg_paths:
            try:
                key = winreg.OpenKey(hkey, subpath)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        name = winreg.EnumKey(key, i)
                        sub = winreg.OpenKey(key, name)
                        dn = self._reg_val(sub, "DisplayName")
                        il = self._reg_val(sub, "InstallLocation")
                        us = self._reg_val(sub, "UninstallString")
                        es = self._reg_val(sub, "EstimatedSize")
                        if dn and il:
                            entries.append((dn, il, us, es, f"{subpath}\\{name}"))
                        winreg.CloseKey(sub)
                    except OSError:
                        pass
                winreg.CloseKey(key)
            except OSError:
                pass
        found = 0
        total = max(1, len(entries))
        for i, (dn, il, us, es, rp) in enumerate(entries):
            if self._cancel:
                break
            self.progress.emit(int((i / total) * 100), f"[{i+1}/{total}] {dn}")
            if il and not os.path.exists(il):
                exe_ok = False
                if us:
                    exe_path = us.strip('"').split('"')[0] if '"' in us else us.split()[0]
                    if os.path.isfile(exe_path):
                        exe_ok = True
                if not exe_ok:
                    est = int(es) * 1024 if es else 0
                    self._emit(f"{dn} → {il}", est, "Phantom (registry only)", "phantom", rp)
                    found += 1
                    self._log(f"PHANTOM: {dn}")
        self.progress.emit(100, f"Phantoms: {found}")
        if found == 0:
            self.finished_scan.emit(T("rec_no_phantom"))
        else:
            self.finished_scan.emit(T("rec_phantom", n=found))

    # ──────────── ORPHAN FOLDERS ────────────
    def _scan_orphans(self):
        known = set()
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        for hkey, subpath in reg_paths:
            try:
                key = winreg.OpenKey(hkey, subpath)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        sub = winreg.OpenKey(key, winreg.EnumKey(key, i))
                        il = self._reg_val(sub, "InstallLocation")
                        if il:
                            known.add(il.rstrip("\\").lower())
                        winreg.CloseKey(sub)
                    except OSError:
                        pass
                winreg.CloseKey(key)
            except OSError:
                pass

        check_roots = [r"C:\Program Files", r"C:\Program Files (x86)", r"C:\Games"]
        all_dirs = []
        for cr in check_roots:
            if os.path.isdir(cr):
                try:
                    all_dirs.extend(os.path.join(cr, d) for d in os.listdir(cr) if os.path.isdir(os.path.join(cr, d)))
                except PermissionError:
                    pass
        orphans = []
        total = max(1, len(all_dirs))
        skip = {"windowsapps","common files","microsoft",".net","dotnet","windows defender",
                "reference assemblies","msbuild","internet explorer","winsxs","nvidia corporation",
                "intel","amd","realtek","google","mozilla maintenance service","vulkanrt"}
        for i, d in enumerate(all_dirs):
            if self._cancel:
                break
            self.progress.emit(int((i / total) * 100), f"[{i+1}/{total}] {os.path.basename(d)}")
            p = d.rstrip("\\").lower()
            if p in known or os.path.basename(d).lower() in skip:
                continue
            sz = get_folder_size(d)
            if sz > 50 * 1024**2:
                orphans.append((d, sz))
                self._log(f"Orphan: {d} ({format_size(sz)})")
        orphans.sort(key=lambda x: x[1], reverse=True)
        for p, sz in orphans:
            self._emit(p, sz, "No uninstaller / App Paths", "orphan")
        total_sz = sum(s for _, s in orphans)
        self.finished_scan.emit(T("rec_orphans", n=len(orphans), sz=format_size(total_sz)))

    # ──────────── INSTALLED PROGRAMS ────────────
    def _scan_installed(self):
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        entries = []
        for hkey, subpath in reg_paths:
            try:
                key = winreg.OpenKey(hkey, subpath)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        name = winreg.EnumKey(key, i)
                        sub = winreg.OpenKey(key, name)
                        dn = self._reg_val(sub, "DisplayName")
                        us = self._reg_val(sub, "UninstallString")
                        sc = self._reg_val(sub, "SystemComponent")
                        pk = self._reg_val(sub, "ParentKeyName")
                        if dn and us and not sc and not pk:
                            pub = self._reg_val(sub, "Publisher") or "—"
                            ver = self._reg_val(sub, "DisplayVersion") or ""
                            es = self._reg_val(sub, "EstimatedSize")
                            il = self._reg_val(sub, "InstallLocation") or ""
                            entries.append((dn, pub, ver, es, il, us))
                        winreg.CloseKey(sub)
                    except OSError:
                        pass
                winreg.CloseKey(key)
            except OSError:
                pass

        computed = []
        total = max(1, len(entries))
        for i, (dn, pub, ver, es, il, us) in enumerate(entries):
            if self._cancel:
                break
            self.progress.emit(int((i / total) * 80), f"[{i+1}/{total}] {dn}")
            sz = int(es) * 1024 if es else 0
            if sz == 0 and il and os.path.isdir(il):
                sz = get_folder_size(il)
            computed.append((dn, pub, ver, sz, us))
        computed.sort(key=lambda x: x[3], reverse=True)
        for dn, pub, ver, sz, us in computed:
            vstr = f" v{ver}" if ver else ""
            self._emit(dn, sz, f"{pub}{vstr}", "installed", us)
        self.progress.emit(100, f"Programs: {len(computed)}")
        self.finished_scan.emit(T("rec_installed", n=len(computed)))

    # ──────────── RECYCLE BIN ────────────
    def _scan_recyclebin(self):
        self.progress.emit(30, "Reading recycle bin...")
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "(New-Object -ComObject Shell.Application).NameSpace(0xA).Items() | "
                 "Measure-Object -Property Size -Sum | Select-Object -ExpandProperty Sum"],
                capture_output=True, text=True, timeout=30
            )
            sz = int(float(result.stdout.strip())) if result.stdout.strip() else 0
        except Exception:
            sz = 0
        if sz > 0:
            self._emit("Recycle Bin", sz, "All drives", "recyclebin")
        self.progress.emit(100, "Done")
        self.finished_scan.emit(T("rec_recycle", sz=format_size(sz)))

    # ──────────── HIBERNATION ────────────
    def _scan_hibernation(self):
        self.progress.emit(50, "Checking hiberfil.sys...")
        hp = r"C:\hiberfil.sys"
        if os.path.exists(hp):
            try:
                sz = os.path.getsize(hp)
                self._emit(hp, sz, "Hibernation file", "hibernation")
                self.finished_scan.emit(T("rec_hiber_on", sz=format_size(sz)))
            except Exception:
                self.finished_scan.emit(T("rec_hiber_err"))
        else:
            self.finished_scan.emit(T("rec_hiber_off"))
        self.progress.emit(100, "Done")

    # ──────────── BROWSER CLEANUP ────────────
    def _scan_browser(self):
        browsers = {
            "Chrome": [
                os.path.join(os.environ.get("LOCALAPPDATA",""), "Google","Chrome","User Data","Default","Cache"),
                os.path.join(os.environ.get("LOCALAPPDATA",""), "Google","Chrome","User Data","Default","Code Cache"),
                os.path.join(os.environ.get("LOCALAPPDATA",""), "Google","Chrome","User Data","Default","GPUCache"),
                os.path.join(os.environ.get("LOCALAPPDATA",""), "Google","Chrome","User Data","Default","Service Worker","CacheStorage"),
            ],
            "Edge": [
                os.path.join(os.environ.get("LOCALAPPDATA",""), "Microsoft","Edge","User Data","Default","Cache"),
                os.path.join(os.environ.get("LOCALAPPDATA",""), "Microsoft","Edge","User Data","Default","Code Cache"),
            ],
            "Firefox": [
                os.path.join(os.environ.get("LOCALAPPDATA",""), "Mozilla","Firefox","Profiles"),
            ],
            "Opera": [
                os.path.join(os.environ.get("APPDATA",""), "Opera Software","Opera Stable","Cache"),
            ],
            "Brave": [
                os.path.join(os.environ.get("LOCALAPPDATA",""), "BraveSoftware","Brave-Browser","User Data","Default","Cache"),
            ],
        }
        total_freed = 0
        items = []
        for browser, paths in browsers.items():
            for p in paths:
                if self._cancel:
                    break
                if os.path.isdir(p):
                    sz = get_folder_size(p)
                    if sz > 512 * 1024:
                        items.append((p, sz, browser))
                        total_freed += sz
        items.sort(key=lambda x: x[1], reverse=True)
        for i, (p, sz, browser) in enumerate(items):
            self.progress.emit(int((i / len(items)) * 100) if items else 100, f"{browser}")
            self._emit(p, sz, f"{browser} cache", "browser")
        self.progress.emit(100, "Done")
        self.finished_scan.emit(T("rec_browser", sz=format_size(total_freed)))

    # ──────────── QUICK AUDIT ────────────
    def _scan_audit(self):
        self.progress.emit(5, "[1/5] Junk...")
        quick_locs = [
            (os.environ.get("TEMP", ""), "User Temp"),
            (r"C:\Windows\Temp", "Windows Temp"),
            (r"C:\Windows\SoftwareDistribution\Download", "Windows Update"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "Google","Chrome","User Data","Default","Cache"), "Chrome"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "Microsoft","Edge","User Data","Default","Cache"), "Edge"),
            (os.path.join(os.environ.get("LOCALAPPDATA",""), "D3DSCache"), "DirectX Cache"),
        ]
        for p, name in quick_locs:
            if self._cancel:
                break
            if p and os.path.isdir(p):
                sz = get_folder_size(p)
                if sz > 1024 * 1024:
                    self._emit(p, sz, f"JUNK: {name}", "junk")

        self.progress.emit(30, "[2/5] Hibernation...")
        if os.path.exists(r"C:\hiberfil.sys"):
            try:
                sz = os.path.getsize(r"C:\hiberfil.sys")
                self._emit(r"C:\hiberfil.sys", sz, "HIBERNATION", "hibernation")
            except Exception:
                pass

        self.progress.emit(50, "[3/5] Recycle bin...")
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "(New-Object -ComObject Shell.Application).NameSpace(0xA).Items() | "
                 "Measure-Object -Property Size -Sum | Select-Object -ExpandProperty Sum"],
                capture_output=True, text=True, timeout=15
            )
            rb_sz = int(float(result.stdout.strip())) if result.stdout.strip() else 0
            if rb_sz > 10 * 1024**2:
                self._emit("Recycle Bin", rb_sz, "RECYCLE", "recyclebin")
        except Exception:
            pass

        self.progress.emit(70, "[4/5] Phantoms...")
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        for hkey, subpath in reg_paths:
            try:
                key = winreg.OpenKey(hkey, subpath)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    if self._cancel:
                        break
                    try:
                        name = winreg.EnumKey(key, i)
                        sub = winreg.OpenKey(key, name)
                        dn = self._reg_val(sub, "DisplayName")
                        il = self._reg_val(sub, "InstallLocation")
                        us = self._reg_val(sub, "UninstallString")
                        es = self._reg_val(sub, "EstimatedSize")
                        if dn and il and not os.path.exists(il):
                            exe_ok = False
                            if us:
                                ep = us.strip('"').split('"')[0] if '"' in us else us.split()[0]
                                if os.path.isfile(ep):
                                    exe_ok = True
                            if not exe_ok:
                                est = int(es) * 1024 if es else 0
                                self._emit(f"{dn} → {il}", est, "PHANTOM", "phantom", f"{subpath}\\{name}")
                        winreg.CloseKey(sub)
                    except OSError:
                        pass
                winreg.CloseKey(key)
            except OSError:
                pass

        self.progress.emit(90, "[5/5] Browser caches...")
        for browser, p in [("Chrome", os.path.join(os.environ.get("LOCALAPPDATA",""), "Google","Chrome","User Data","Default","Cache")),
                           ("Firefox", os.path.join(os.environ.get("LOCALAPPDATA",""), "Mozilla","Firefox","Profiles"))]:
            if os.path.isdir(p):
                sz = get_folder_size(p)
                if sz > 5 * 1024**2:
                    self._emit(p, sz, f"BROWSER: {browser}", "browser")

        self.progress.emit(100, "Audit complete")
        self.finished_scan.emit(T("rec_audit"))

    # ──────────── CUSTOM SCAN ────────────
    def _scan_custom(self):
        path = self.extra
        if not path or not os.path.isdir(path):
            self.finished_scan.emit(T("rec_path_err"))
            return
        items = []
        try:
            for name in os.listdir(path):
                if self._cancel:
                    break
                fp = os.path.join(path, name)
                if os.path.isdir(fp):
                    sz = get_folder_size(fp)
                    items.append((fp, sz, "Folder", "folder"))
                elif os.path.isfile(fp):
                    sz = os.path.getsize(fp)
                    items.append((fp, sz, "File", "file"))
        except PermissionError:
            pass
        items.sort(key=lambda x: x[1], reverse=True)
        for fp, sz, det, tp in items[:100]:
            self._emit(fp, sz, det, tp)
            self.progress.emit(min(100, items.index((fp, sz, det, tp)) * 100 // max(1, len(items))), os.path.basename(fp))
        self.progress.emit(100, "Done")
        total_sz = sum(s for _, s, _, _ in items[:100])
        self.finished_scan.emit(T("rec_custom", n=len(items[:100]), sz=format_size(total_sz)))

    # ── registry helper ──
    def _reg_val(self, key, name):
        try:
            return winreg.QueryValueEx(key, name)[0]
        except (OSError, FileNotFoundError):
            return None


# ═══════════════════════════════════════════════════
#  OPTIMIZATION DEFINITIONS
# ═══════════════════════════════════════════════════
def get_opt_presets():
    """Return optimization presets with translated strings."""
    return {
        "light": {
            "title": T("opt_light"),
            "desc": T("opt_light_d"),
            "color": C.GREEN,
            "actions": [
                (T("oa_temp"), "powershell -NoProfile -Command \"Get-ChildItem $env:TEMP -Force -EA SilentlyContinue | Remove-Item -Recurse -Force -EA SilentlyContinue; Get-ChildItem 'C:\\Windows\\Temp' -Force -EA SilentlyContinue | Remove-Item -Recurse -Force -EA SilentlyContinue; Get-ChildItem 'C:\\Windows\\Prefetch' -Force -EA SilentlyContinue | Remove-Item -Force -EA SilentlyContinue\""),
                (T("oa_menu"), 'reg add "HKCU\\Control Panel\\Desktop" /v MenuShowDelay /t REG_SZ /d "0" /f'),
                (T("oa_dns"), "ipconfig /flushdns"),
                (T("oa_fastboot"), 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v HiberbootEnabled /t REG_DWORD /d 1 /f'),
            ],
        },
        "medium": {
            "title": T("opt_medium"),
            "desc": T("opt_medium_d"),
            "color": C.ORANGE,
            "actions": [
                (T("oa_telemetry"), 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && sc stop DiagTrack >nul 2>&1 && sc config DiagTrack start=disabled >nul 2>&1'),
                (T("oa_cortana"), 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f'),
                (T("oa_ads"), 'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f'),
                (T("oa_tips"), 'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v SubscribedContent-338388Enabled /t REG_DWORD /d 0 /f'),
                (T("oa_eventlogs"), "powershell -NoProfile -Command \"wevtutil el 2>$null | ForEach-Object { wevtutil cl $_ 2>$null }\""),
            ],
        },
        "heavy": {
            "title": T("opt_heavy"),
            "desc": T("opt_heavy_d"),
            "color": C.RED,
            "actions": [
                (T("oa_visual"), 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f'),
                (T("oa_sysmain"), "sc stop SysMain >nul 2>&1 && sc config SysMain start=disabled >nul 2>&1"),
                (T("oa_wsearch"), "sc stop WSearch >nul 2>&1 && sc config WSearch start=disabled >nul 2>&1"),
                (T("oa_hibernate"), "powercfg /h off"),
                (T("oa_power"), "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"),
                (T("oa_diagtrack"), "sc stop DiagTrack >nul 2>&1 && sc config DiagTrack start=disabled >nul 2>&1"),
            ],
        },
    }


# ═══════════════════════════════════════════════════
#  ANIMATED BACKGROUND WIDGET — Neon Grid + Particles
# ═══════════════════════════════════════════════════
class CyberBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._t = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)
        import random
        self._particles = [
            {"x": random.random(), "y": random.random(),
             "vx": (random.random() - 0.5) * 0.002,
             "vy": (random.random() - 0.5) * 0.002,
             "r": random.random() * 2 + 1,
             "c": random.choice([C.CYAN, C.PINK, C.PURPLE])}
            for _ in range(40)
        ]
        self._lines = [
            {"x": random.random(), "speed": 0.001 + random.random() * 0.003,
             "alpha": 0.03 + random.random() * 0.06,
             "len": 0.05 + random.random() * 0.15}
            for _ in range(15)
        ]

    def _tick(self):
        self._t += 1
        import math, random
        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] < 0 or p["x"] > 1:
                p["vx"] *= -1
            if p["y"] < 0 or p["y"] > 1:
                p["vy"] *= -1
        for l in self._lines:
            l["x"] += l["speed"]
            if l["x"] > 1.2:
                l["x"] = -0.2
        self.update()

    def paintEvent(self, event):
        import math
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Grid lines
        grid_pen = QPen(QColor(C.CYAN))
        grid_pen.setWidthF(0.5)
        for gx in range(0, w, 60):
            alpha = 0.03 + 0.02 * math.sin(self._t * 0.02 + gx * 0.01)
            c = QColor(C.CYAN)
            c.setAlphaF(alpha)
            grid_pen.setColor(c)
            p.setPen(grid_pen)
            p.drawLine(gx, 0, gx, h)
        for gy in range(0, h, 60):
            alpha = 0.03 + 0.02 * math.sin(self._t * 0.02 + gy * 0.01)
            c = QColor(C.CYAN)
            c.setAlphaF(alpha)
            grid_pen.setColor(c)
            p.setPen(grid_pen)
            p.drawLine(0, gy, w, gy)

        # Vertical neon lines
        for l in self._lines:
            x = int(l["x"] * w)
            y1 = 0
            y2 = int(l["len"] * h)
            grad = QLinearGradient(x, y1, x, y2)
            c = QColor(C.PINK)
            c.setAlphaF(0)
            grad.setColorAt(0, c)
            c2 = QColor(C.PINK)
            c2.setAlphaF(l["alpha"])
            grad.setColorAt(0.5, c2)
            c3 = QColor(C.PINK)
            c3.setAlphaF(0)
            grad.setColorAt(1, c3)
            pen = QPen(QBrush(grad), 1.5)
            p.setPen(pen)
            p.drawLine(x, y1, x, y2)

        # Particles
        p.setPen(Qt.NoPen)
        for pt in self._particles:
            x = int(pt["x"] * w)
            y = int(pt["y"] * h)
            c = QColor(pt["c"])
            c.setAlphaF(0.4 + 0.3 * math.sin(self._t * 0.05 + x))
            p.setBrush(c)
            p.drawEllipse(QPoint(x, y), int(pt["r"]), int(pt["r"]))
            # Glow
            gc = QColor(pt["c"])
            gc.setAlphaF(0.08)
            p.setBrush(gc)
            p.drawEllipse(QPoint(x, y), int(pt["r"] * 4), int(pt["r"] * 4))

        p.end()


# ═══════════════════════════════════════════════════
#  NEON PROGRESS BAR
# ═══════════════════════════════════════════════════
class NeonProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(8)
        self._value = 0
        self._anim_offset = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._pulse)
        self._timer.start(40)

    def _pulse(self):
        if 0 < self._value < 100:
            self._anim_offset = (self._anim_offset + 2) % 40
            self.update()

    def setValue(self, v):
        self._value = max(0, min(100, v))
        self.update()

    def paintEvent(self, event):
        import math
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        # Background
        p.setBrush(QColor(C.PANEL2))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, w, h, 4, 4)
        # Fill
        fw = int(w * self._value / 100)
        if fw > 0:
            grad = QLinearGradient(0, 0, fw, 0)
            grad.setColorAt(0, QColor(C.CYAN))
            grad.setColorAt(0.5, QColor(C.PURPLE))
            grad.setColorAt(1, QColor(C.PINK))
            p.setBrush(grad)
            p.drawRoundedRect(0, 0, fw, h, 4, 4)
            # Glow effect
            if self._value < 100:
                gc = QColor(C.CYAN)
                gc.setAlphaF(0.15 + 0.1 * math.sin(self._anim_offset * 0.15))
                p.setBrush(gc)
                p.drawRoundedRect(max(0, fw - 30), 0, 30, h, 4, 4)
        p.end()


# ═══════════════════════════════════════════════════
#  SIDEBAR BUTTON
# ═══════════════════════════════════════════════════
class SidebarButton(QPushButton):
    def __init__(self, text, icon_text="", accent=C.CYAN, parent=None):
        super().__init__(parent)
        self._text = text
        self._icon_text = icon_text
        self._accent = accent
        self._active = False
        self._hover = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(46)
        self.setStyleSheet("background: transparent; border: none;")

    def set_active(self, active):
        self._active = active
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        if self._active:
            # Active — gradient bg + left neon bar + subtle glow
            grad = QLinearGradient(0, 0, w, 0)
            ac = QColor(self._accent)
            ac.setAlphaF(0.18)
            grad.setColorAt(0, ac)
            ac2 = QColor(self._accent)
            ac2.setAlphaF(0.03)
            grad.setColorAt(1, ac2)
            p.setBrush(grad)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(4, 2, w - 8, h - 4, 10, 10)
            # Left neon bar
            bar_grad = QLinearGradient(0, 6, 0, h - 6)
            bar_grad.setColorAt(0, QColor(self._accent))
            bc = QColor(self._accent)
            bc.setAlphaF(0.3)
            bar_grad.setColorAt(1, bc)
            p.setBrush(bar_grad)
            p.drawRoundedRect(0, 6, 3, h - 12, 2, 2)
        elif self.underMouse():
            hc = QColor(C.PANEL3)
            hc.setAlphaF(0.7)
            p.setBrush(hc)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(4, 2, w - 8, h - 4, 10, 10)

        # Icon
        p.setFont(QFont("Segoe UI", 13))
        p.setPen(QColor(self._accent if self._active else C.MUTED))
        p.drawText(QRect(14, 0, 30, h), Qt.AlignCenter, self._icon_text)

        # Text
        f = QFont("Segoe UI", 10)
        f.setBold(self._active)
        f.setLetterSpacing(QFont.AbsoluteSpacing, 0.5 if self._active else 0)
        p.setFont(f)
        p.setPen(QColor(C.TEXT if self._active else C.DIM))
        p.drawText(QRect(48, 0, w - 58, h), Qt.AlignVCenter | Qt.AlignLeft, self._text)
        p.end()

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()


# ═══════════════════════════════════════════════════
#  STAT CARD
# ═══════════════════════════════════════════════════
class StatCard(QFrame):
    def __init__(self, label, value, accent=C.CYAN, parent=None):
        super().__init__(parent)
        self.setFixedHeight(74)
        self.setMinimumWidth(140)
        self._accent = accent
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {C.PANEL2}, stop:1 {C.PANEL});
                border: 1px solid {C.BORDER};
                border-radius: 10px;
                border-top: 2px solid {accent};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(2)
        self._lbl = QLabel(label)
        self._lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self._lbl.setStyleSheet(f"color: {C.MUTED}; border: none; letter-spacing: 2px;")
        self._val = QLabel(value)
        self._val.setFont(QFont("Consolas", 18, QFont.Black))
        self._val.setStyleSheet(f"color: {accent}; border: none;")
        layout.addWidget(self._lbl)
        layout.addWidget(self._val)

    def set_value(self, v):
        self._val.setText(v)

    def set_color(self, c):
        self._val.setStyleSheet(f"color: {c}; border: none;")


# ═══════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"s0meClean? v{VERSION}")
        self.setMinimumSize(1300, 800)
        self.resize(1400, 880)
        self._worker = None
        self._scan_items: List[ScanItem] = []

        # ── Central widget ──
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet(f"background-color: {C.BG}; color: {C.TEXT};")

        # ── Background animation ──
        self._bg = CyberBackground(central)
        self._bg.setGeometry(0, 0, 2000, 2000)
        self._bg.lower()

        # ── Main layout ──
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Header ──
        self._build_header(main_layout)

        # ── Body (sidebar + content) ──
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._build_sidebar(body)
        self._build_content(body)

        main_layout.addLayout(body, 1)

        # ── Status bar ──
        self._build_statusbar(main_layout)

        # ── Init ──
        self._switch_tab("clean")
        self._update_disk_info()

    # ── HEADER ──
    def _build_header(self, parent_layout):
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.PANEL}, stop:0.5 {C.PANEL2}, stop:1 {C.PANEL});
                border-bottom: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.CYAN}, stop:0.5 {C.PINK}, stop:1 {C.PURPLE});
            }}
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 10, 20, 10)

        # Logo
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(2)
        title = QLabel("s0meClean?")
        title.setFont(QFont("Consolas", 22, QFont.Black))
        title.setStyleSheet(f"color: {C.CYAN}; background: transparent;")
        subtitle = QLabel(T("subtitle"))
        subtitle.setFont(QFont("Segoe UI", 9, QFont.Bold))
        subtitle.setStyleSheet(f"color: {C.PINK}; background: transparent; letter-spacing: 3px;")
        logo_layout.addWidget(title)
        logo_layout.addWidget(subtitle)
        hl.addLayout(logo_layout)

        hl.addSpacing(40)

        # Drive selector
        drive_layout = QVBoxLayout()
        dl = QLabel(T("drive"))
        dl.setFont(QFont("Consolas", 8, QFont.Bold))
        dl.setStyleSheet(f"color: {C.MUTED}; background: transparent;")
        self._drive_combo = QComboBox()
        self._drive_combo.setFont(QFont("Consolas", 14, QFont.Bold))
        self._drive_combo.setStyleSheet(f"""
            QComboBox {{
                background: {C.PANEL2}; color: {C.CYAN}; border: 1px solid {C.BORDER};
                border-radius: 6px; padding: 4px 10px; min-width: 70px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{ background: {C.PANEL2}; color: {C.TEXT}; selection-background-color: {C.CYAN_D}; }}
        """)
        import string
        for letter in string.ascii_uppercase:
            drive = f"{letter}:"
            if os.path.isdir(drive + "\\"):
                self._drive_combo.addItem(drive)
        idx = self._drive_combo.findText("C:")
        if idx >= 0:
            self._drive_combo.setCurrentIndex(idx)
        self._drive_combo.currentTextChanged.connect(self._on_drive_changed)
        drive_layout.addWidget(dl)
        drive_layout.addWidget(self._drive_combo)
        hl.addLayout(drive_layout)

        hl.addSpacing(30)

        # Stats
        self._stat_total = StatCard(T("total"), "—", C.TEXT)
        self._stat_used = StatCard(T("used"), "—", C.TEXT)
        self._stat_free = StatCard(T("free"), "—", C.GREEN)
        hl.addWidget(self._stat_total)
        hl.addWidget(self._stat_used)
        hl.addWidget(self._stat_free)

        hl.addStretch()

        # Admin badge
        admin_badge = QLabel(T("admin_yes") if is_admin() else T("admin_no"))
        admin_badge.setFont(QFont("Consolas", 10, QFont.Bold))
        admin_badge.setStyleSheet(f"color: {C.GREEN if is_admin() else C.RED}; background: transparent;")
        hl.addWidget(admin_badge)

        # Version badge
        ver_badge = QLabel(f"v{VERSION}")
        ver_badge.setFont(QFont("Consolas", 9))
        ver_badge.setStyleSheet(f"""
            color: {C.CYAN}; background: {C.PANEL2}; border: 1px solid {C.CYAN_D};
            border-radius: 10px; padding: 2px 12px;
        """)
        hl.addWidget(ver_badge)

        parent_layout.addWidget(header)

    # ── SIDEBAR ──
    def _build_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {C.PANEL}, stop:1 {C.BG2});
                border-right: 1px solid {C.BORDER};
            }}
        """)
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(8, 12, 8, 12)
        sl.setSpacing(4)

        self._sidebar_btns = {}
        tabs = [
            ("clean", T("tab_clean"), "🧹", C.CYAN),
            ("opt", T("tab_opt"), "⚡", C.ORANGE),
            ("browser", T("tab_browser"), "🌐", C.PURPLE),
            ("custom", T("tab_custom"), "📁", C.PINK),
            ("settings", T("tab_settings"), "⚙", C.DIM),
        ]
        for key, text, icon, color in tabs:
            btn = SidebarButton(text, icon, color)
            btn.clicked.connect(lambda checked=False, k=key: self._switch_tab(k))
            sl.addWidget(btn)
            self._sidebar_btns[key] = btn

        sl.addSpacing(12)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {C.BORDER};")
        sl.addWidget(sep)
        sl.addSpacing(8)

        # Scan actions label
        self._actions_label = QLabel(T("scan_actions"))
        self._actions_label.setFont(QFont("Consolas", 8, QFont.Bold))
        self._actions_label.setStyleSheet(f"color: {C.PINK}; background: transparent;")
        sl.addWidget(self._actions_label)
        sl.addSpacing(4)

        # Action buttons container
        self._action_container = QVBoxLayout()
        self._action_container.setSpacing(4)
        sl.addLayout(self._action_container)

        sl.addStretch()

        # GitHub button
        gh_btn = QPushButton(T("github_btn"))
        gh_btn.setCursor(Qt.PointingHandCursor)
        gh_btn.setFont(QFont("Segoe UI", 9, QFont.Bold))
        gh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL2}; color: {C.DIM}; border: 1px solid {C.BORDER};
                border-radius: 10px; padding: 10px;
            }}
            QPushButton:hover {{
                color: {C.CYAN}; border-color: {C.CYAN};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0,240,255,0.08), stop:1 {C.PANEL2});
            }}
        """)
        gh_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f"https://github.com/{GITHUB_REPO}")))
        sl.addWidget(gh_btn)

        # Update button
        upd_btn = QPushButton(T("check_updates"))
        upd_btn.setCursor(Qt.PointingHandCursor)
        upd_btn.setFont(QFont("Segoe UI", 9, QFont.Bold))
        upd_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL2}; color: {C.DIM}; border: 1px solid {C.BORDER};
                border-radius: 10px; padding: 10px;
            }}
            QPushButton:hover {{
                color: {C.GREEN}; border-color: {C.GREEN};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(50,230,130,0.08), stop:1 {C.PANEL2});
            }}
        """)
        upd_btn.clicked.connect(self._check_update)
        sl.addWidget(upd_btn)

        parent_layout.addWidget(sidebar)

    # ── CONTENT AREA ──
    def _build_content(self, parent_layout):
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background: {C.BG};")

        # Pages
        self._page_clean = self._build_clean_page()
        self._page_opt = self._build_opt_page()
        self._page_browser = self._build_browser_page()
        self._page_custom = self._build_custom_page()
        self._page_settings = self._build_settings_page()

        self._stack.addWidget(self._page_clean)
        self._stack.addWidget(self._page_opt)
        self._stack.addWidget(self._page_browser)
        self._stack.addWidget(self._page_custom)
        self._stack.addWidget(self._page_settings)

        parent_layout.addWidget(self._stack, 1)

    # ── CLEAN PAGE ──
    def _build_clean_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 12, 16, 8)
        layout.setSpacing(8)

        # Top bar
        top = QHBoxLayout()
        t = QLabel(T("results"))
        t.setFont(QFont("Consolas", 12, QFont.Bold))
        t.setStyleSheet(f"color: {C.CYAN};")
        top.addWidget(t)
        top.addStretch()
        self._result_info = QLabel("")
        self._result_info.setFont(QFont("Consolas", 9))
        self._result_info.setStyleSheet(f"color: {C.DIM};")
        top.addWidget(self._result_info)
        layout.addLayout(top)

        # Progress bar
        self._progress = NeonProgressBar()
        layout.addWidget(self._progress)

        # Recommendation box
        rec_frame = QFrame()
        rec_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.PANEL}, stop:1 {C.PANEL2});
                border: 1px solid {C.BORDER}; border-radius: 10px;
                border-left: 3px solid {C.PINK};
            }}
        """)
        rec_layout = QHBoxLayout(rec_frame)
        rec_layout.setContentsMargins(12, 8, 12, 8)
        # Pink stripe
        stripe = QFrame()
        stripe.setFixedWidth(3)
        stripe.setStyleSheet(f"background: {C.PINK}; border: none; border-radius: 1px;")
        rec_layout.addWidget(stripe)
        rec_inner = QVBoxLayout()
        rl = QLabel(T("analysis"))
        rl.setFont(QFont("Consolas", 8, QFont.Bold))
        rl.setStyleSheet(f"color: {C.PINK}; border: none;")
        self._rec_text = QLabel(T("start_hint"))
        self._rec_text.setFont(QFont("Segoe UI", 10))
        self._rec_text.setStyleSheet(f"color: {C.TEXT}; border: none;")
        self._rec_text.setWordWrap(True)
        rec_inner.addWidget(rl)
        rec_inner.addWidget(self._rec_text)
        rec_layout.addLayout(rec_inner, 1)
        layout.addWidget(rec_frame)

        # Tree (results list)
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["#", T("col_size"), T("col_path"), T("col_type")])
        self._tree.setColumnWidth(0, 50)
        self._tree.setColumnWidth(1, 120)
        self._tree.setColumnWidth(2, 650)
        self._tree.setColumnWidth(3, 250)
        self._tree.setAlternatingRowColors(True)
        self._tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self._tree.setRootIsDecorated(False)
        self._tree.setSortingEnabled(True)
        self._tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {C.PANEL}; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 10px;
                font-family: 'Consolas'; font-size: 10pt;
                alternate-background-color: {C.PANEL2};
                outline: none;
            }}
            QTreeWidget::item {{
                padding: 6px 4px;
                border-bottom: 1px solid rgba(42, 54, 96, 0.5);
            }}
            QTreeWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0,240,255,0.15), stop:1 rgba(168,85,247,0.08));
                border-left: 3px solid {C.CYAN};
            }}
            QTreeWidget::item:hover {{
                background: rgba(0,240,255,0.06);
            }}
            QHeaderView::section {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {C.PANEL3}, stop:1 {C.PANEL2});
                color: {C.CYAN}; border: none;
                font-family: 'Segoe UI'; font-weight: bold; font-size: 9pt;
                padding: 8px 10px; letter-spacing: 1px;
                border-bottom: 2px solid {C.CYAN};
            }}
            QScrollBar:vertical {{
                background: {C.PANEL}; width: 8px; border: none; border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {C.BORDER}; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {C.CYAN_D}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        layout.addWidget(self._tree, 1)

        # Bottom bar
        bottom = QHBoxLayout()
        bottom.setSpacing(12)

        # Log
        log_frame = QFrame()
        log_frame.setStyleSheet(f"QFrame {{ background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 8px; }}")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(10, 6, 10, 6)
        ll = QLabel(T("activity"))
        ll.setFont(QFont("Consolas", 8, QFont.Bold))
        ll.setStyleSheet(f"color: {C.PINK}; border: none;")
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setFont(QFont("Consolas", 9))
        self._log_text.setStyleSheet(f"color: {C.DIM}; background: transparent; border: none;")
        self._log_text.setMaximumHeight(140)
        log_layout.addWidget(ll)
        log_layout.addWidget(self._log_text)
        bottom.addWidget(log_frame, 3)

        # Action buttons
        act_frame = QFrame()
        act_frame.setStyleSheet(f"QFrame {{ background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 8px; }}")
        act_layout = QVBoxLayout(act_frame)
        act_layout.setContentsMargins(12, 8, 12, 8)

        self._sel_label = QLabel(T("nothing_sel"))
        self._sel_label.setFont(QFont("Consolas", 9))
        self._sel_label.setStyleSheet(f"color: {C.MUTED}; border: none;")
        act_layout.addWidget(self._sel_label)

        self._btn_delete = QPushButton(T("delete_sel"))
        self._btn_delete.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self._btn_delete.setCursor(Qt.PointingHandCursor)
        self._btn_delete.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.RED}, stop:1 {C.PINK_D});
                color: white; border: none; border-radius: 10px; padding: 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6080, stop:1 {C.PINK});
            }}
            QPushButton:disabled {{ background: {C.PANEL2}; color: {C.MUTED}; }}
        """)
        self._btn_delete.setEnabled(False)
        self._btn_delete.clicked.connect(self._delete_selected)
        act_layout.addWidget(self._btn_delete)

        btn_open = QPushButton(T("open_explorer"))
        btn_open.setFont(QFont("Segoe UI", 9, QFont.Bold))
        btn_open.setCursor(Qt.PointingHandCursor)
        btn_open.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.CYAN}, stop:1 {C.CYAN_D});
                color: {C.BG}; border: none; border-radius: 10px; padding: 10px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.CYAN_D}, stop:1 {C.CYAN});
            }}
        """)
        btn_open.clicked.connect(self._open_in_explorer)
        act_layout.addWidget(btn_open)

        btn_sel_all = QPushButton(T("select_all"))
        btn_sel_all.setFont(QFont("Segoe UI", 9, QFont.Bold))
        btn_sel_all.setCursor(Qt.PointingHandCursor)
        btn_sel_all.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL2}; color: {C.PINK};
                border: 1px solid rgba(255,30,130,0.3);
                border-radius: 10px; padding: 10px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.PINK}, stop:1 {C.PINK_D});
                color: white; border-color: {C.PINK};
            }}
        """)
        btn_sel_all.clicked.connect(self._select_all)
        act_layout.addWidget(btn_sel_all)

        bottom.addWidget(act_frame, 2)
        layout.addLayout(bottom)

        # Selection changed
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)

        return page

    # ── OPTIMIZATION PAGE ──
    def _build_opt_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)

        t = QLabel(T("opt_title"))
        t.setFont(QFont("Consolas", 16, QFont.Bold))
        t.setStyleSheet(f"color: {C.CYAN};")
        layout.addWidget(t)

        desc = QLabel(T("opt_desc"))
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {C.DIM};")
        layout.addWidget(desc)
        layout.addSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ background: transparent; border: none; }}")
        scroll_w = QWidget()
        scroll_l = QVBoxLayout(scroll_w)
        scroll_l.setSpacing(16)

        for key, preset in get_opt_presets().items():
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: {C.PANEL}; border: 1px solid {C.BORDER};
                    border-radius: 12px; border-left: 4px solid {preset['color']};
                }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)

            # Title row
            tr = QHBoxLayout()
            tt = QLabel(preset["title"])
            tt.setFont(QFont("Consolas", 14, QFont.Bold))
            tt.setStyleSheet(f"color: {preset['color']}; border: none;")
            tr.addWidget(tt)
            tr.addStretch()
            apply_btn = QPushButton(T("apply"))
            apply_btn.setFont(QFont("Consolas", 10, QFont.Bold))
            apply_btn.setCursor(Qt.PointingHandCursor)
            apply_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {preset['color']}; color: {C.BG}; border: none;
                    border-radius: 8px; padding: 8px 24px;
                }}
                QPushButton:hover {{ opacity: 0.9; }}
            """)
            tr.addWidget(apply_btn)
            cl.addLayout(tr)

            dd = QLabel(preset["desc"])
            dd.setFont(QFont("Segoe UI", 9))
            dd.setStyleSheet(f"color: {C.DIM}; border: none;")
            cl.addWidget(dd)
            cl.addSpacing(6)

            checks = []
            for action_name, cmd in preset["actions"]:
                cb = QCheckBox(action_name)
                cb.setChecked(True)
                cb.setFont(QFont("Segoe UI", 9.5))
                cb.setStyleSheet(f"color: {C.TEXT}; border: none; spacing: 8px;")
                cb.setProperty("cmd", cmd)
                cl.addWidget(cb)
                checks.append(cb)

            apply_btn.clicked.connect(lambda checked=False, ch=checks, title=preset["title"]: self._apply_opt(ch, title))
            scroll_l.addWidget(card)

        # Quick actions
        qa_frame = QFrame()
        qa_frame.setStyleSheet(f"QFrame {{ background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 12px; }}")
        qa_l = QVBoxLayout(qa_frame)
        qa_l.setContentsMargins(16, 12, 16, 12)
        qa_t = QLabel(T("quick_actions"))
        qa_t.setFont(QFont("Consolas", 11, QFont.Bold))
        qa_t.setStyleSheet(f"color: {C.YELLOW}; border: none;")
        qa_l.addWidget(qa_t)

        quick_actions = [
            (T("qa_chkdsk"), "chkdsk C:"),
            (T("qa_cleanmgr"), "cleanmgr /lowdisk"),
            (T("qa_defrag"), "dfrgui"),
            (T("qa_startup"), "taskmgr /0 /startup"),
            (T("qa_services"), "services.msc"),
        ]
        for label, cmd in quick_actions:
            btn = QPushButton(f"  {label}")
            btn.setFont(QFont("Consolas", 9))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C.PANEL2}; color: {C.CYAN}; border: none;
                    border-radius: 6px; padding: 8px; text-align: left;
                }}
                QPushButton:hover {{ background: {C.PANEL3}; }}
            """)
            btn.clicked.connect(lambda checked=False, c=cmd: subprocess.Popen(c, shell=True))
            qa_l.addWidget(btn)

        scroll_l.addWidget(qa_frame)
        scroll_l.addStretch()
        scroll.setWidget(scroll_w)
        layout.addWidget(scroll, 1)

        return page

    # ── BROWSER PAGE ──
    def _build_browser_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)

        t = QLabel(T("browser_title"))
        t.setFont(QFont("Consolas", 16, QFont.Bold))
        t.setStyleSheet(f"color: {C.PURPLE};")
        layout.addWidget(t)

        desc = QLabel(T("browser_desc"))
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {C.DIM};")
        layout.addWidget(desc)
        layout.addSpacing(16)

        scan_btn = QPushButton(T("scan_browsers"))
        scan_btn.setFont(QFont("Consolas", 11, QFont.Bold))
        scan_btn.setCursor(Qt.PointingHandCursor)
        scan_btn.setFixedHeight(48)
        scan_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.PURPLE}; color: white; border: none;
                border-radius: 10px; padding: 12px;
            }}
            QPushButton:hover {{ background: #b967ff; }}
        """)
        scan_btn.clicked.connect(lambda: self._start_scan("browser"))
        layout.addWidget(scan_btn)

        info = QLabel(T("browser_hint"))
        info.setFont(QFont("Segoe UI", 9))
        info.setStyleSheet(f"color: {C.MUTED};")
        layout.addWidget(info)
        layout.addStretch()

        return page

    # ── CUSTOM SCAN PAGE ──
    def _build_custom_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)

        t = QLabel(T("custom_title"))
        t.setFont(QFont("Consolas", 16, QFont.Bold))
        t.setStyleSheet(f"color: {C.PINK};")
        layout.addWidget(t)

        desc = QLabel(T("custom_desc"))
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {C.DIM};")
        layout.addWidget(desc)
        layout.addSpacing(16)

        # Path row
        row = QHBoxLayout()
        pl = QLabel(T("path_label"))
        pl.setFont(QFont("Consolas", 10, QFont.Bold))
        pl.setStyleSheet(f"color: {C.PINK};")
        row.addWidget(pl)
        self._custom_path = QLineEdit()
        self._custom_path.setFont(QFont("Consolas", 10))
        self._custom_path.setStyleSheet(f"""
            QLineEdit {{
                background: {C.PANEL2}; color: {C.TEXT}; border: 1px solid {C.BORDER};
                border-radius: 6px; padding: 8px;
            }}
        """)
        row.addWidget(self._custom_path, 1)

        pick_btn = QPushButton(T("pick_folder"))
        pick_btn.setFont(QFont("Consolas", 9, QFont.Bold))
        pick_btn.setCursor(Qt.PointingHandCursor)
        pick_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL}; color: {C.CYAN}; border: 1px solid {C.CYAN};
                border-radius: 6px; padding: 8px 16px;
            }}
            QPushButton:hover {{ background: {C.CYAN}; color: {C.BG}; }}
        """)
        pick_btn.clicked.connect(self._pick_custom_folder)
        row.addWidget(pick_btn)

        scan_btn = QPushButton(T("scan_go"))
        scan_btn.setFont(QFont("Consolas", 9, QFont.Bold))
        scan_btn.setCursor(Qt.PointingHandCursor)
        scan_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.CYAN}; color: {C.BG}; border: none;
                border-radius: 6px; padding: 8px 16px;
            }}
            QPushButton:hover {{ background: {C.CYAN_D}; }}
        """)
        scan_btn.clicked.connect(lambda: self._start_scan("custom", self._custom_path.text()))
        row.addWidget(scan_btn)

        layout.addLayout(row)
        layout.addSpacing(12)

        hint = QLabel(T("custom_hint"))
        hint.setFont(QFont("Segoe UI", 10, italic=True))
        hint.setStyleSheet(f"color: {C.MUTED};")
        layout.addWidget(hint)
        layout.addStretch()

        return page

    # ── SETTINGS PAGE ──
    def _build_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)

        t = QLabel(T("settings_title"))
        t.setFont(QFont("Consolas", 16, QFont.Bold))
        t.setStyleSheet(f"color: {C.CYAN};")
        layout.addWidget(t)
        layout.addSpacing(16)

        # Language card
        lang_card = QFrame()
        lang_card.setStyleSheet(f"""
            QFrame {{
                background: {C.PANEL}; border: 1px solid {C.BORDER};
                border-radius: 12px; border-left: 4px solid {C.PURPLE};
            }}
        """)
        lang_l = QVBoxLayout(lang_card)
        lang_l.setContentsMargins(16, 12, 16, 12)
        lang_t = QLabel(T("language"))
        lang_t.setFont(QFont("Consolas", 11, QFont.Bold))
        lang_t.setStyleSheet(f"color: {C.PURPLE}; border: none;")
        lang_l.addWidget(lang_t)
        lang_row = QHBoxLayout()
        self._lang_combo = QComboBox()
        self._lang_combo.addItem("English", "EN")
        self._lang_combo.addItem("Русский", "RU")
        idx_lang = self._lang_combo.findData(LANG)
        if idx_lang >= 0:
            self._lang_combo.setCurrentIndex(idx_lang)
        self._lang_combo.setFont(QFont("Consolas", 11))
        self._lang_combo.setStyleSheet(f"""
            QComboBox {{
                background: {C.PANEL2}; color: {C.CYAN}; border: 1px solid {C.BORDER};
                border-radius: 6px; padding: 6px 12px; min-width: 160px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{ background: {C.PANEL2}; color: {C.TEXT}; selection-background-color: {C.CYAN_D}; }}
        """)
        self._lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self._lang_combo)
        self._lang_hint = QLabel(T("lang_restart"))
        self._lang_hint.setFont(QFont("Segoe UI", 9))
        self._lang_hint.setStyleSheet(f"color: {C.MUTED}; border: none;")
        self._lang_hint.setVisible(False)
        lang_row.addWidget(self._lang_hint)
        lang_row.addStretch()
        lang_l.addLayout(lang_row)
        layout.addWidget(lang_card)
        layout.addSpacing(12)

        # About card
        about = QFrame()
        about.setStyleSheet(f"""
            QFrame {{
                background: {C.PANEL}; border: 1px solid {C.BORDER};
                border-radius: 12px; border-left: 4px solid {C.GREEN};
            }}
        """)
        al = QVBoxLayout(about)
        al.setContentsMargins(16, 12, 16, 12)
        at = QLabel(T("about"))
        at.setFont(QFont("Consolas", 11, QFont.Bold))
        at.setStyleSheet(f"color: {C.GREEN}; border: none;")
        al.addWidget(at)
        ad = QLabel(f"s0meClean? v{VERSION}\n{T('about_text')}")
        ad.setFont(QFont("Segoe UI", 10))
        ad.setStyleSheet(f"color: {C.DIM}; border: none;")
        ad.setWordWrap(True)
        al.addWidget(ad)
        layout.addWidget(about)
        layout.addSpacing(12)

        # Key activation
        key_card = QFrame()
        key_card.setStyleSheet(f"""
            QFrame {{
                background: {C.PANEL}; border: 1px solid {C.BORDER};
                border-radius: 12px; border-left: 4px solid {C.CYAN};
            }}
        """)
        kl = QVBoxLayout(key_card)
        kl.setContentsMargins(16, 12, 16, 12)
        kt = QLabel(T("access_key"))
        kt.setFont(QFont("Consolas", 11, QFont.Bold))
        kt.setStyleSheet(f"color: {C.CYAN}; border: none;")
        kl.addWidget(kt)

        key_row = QHBoxLayout()
        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("XXXXX-XXXXX-XXXXX-XXXXX-XXXXX")
        self._key_input.setFont(QFont("Consolas", 12))
        self._key_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C.PANEL2}; color: {C.TEXT}; border: 1px solid {C.BORDER};
                border-radius: 6px; padding: 8px; letter-spacing: 2px;
            }}
        """)
        key_row.addWidget(self._key_input, 1)
        activate_btn = QPushButton(T("activate"))
        activate_btn.setFont(QFont("Consolas", 10, QFont.Bold))
        activate_btn.setCursor(Qt.PointingHandCursor)
        activate_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.CYAN}; color: {C.BG}; border: none;
                border-radius: 6px; padding: 8px 20px;
            }}
            QPushButton:hover {{ background: {C.CYAN_D}; }}
        """)
        activate_btn.clicked.connect(self._activate_key)
        key_row.addWidget(activate_btn)
        kl.addLayout(key_row)

        self._key_status = QLabel(T("key_none"))
        self._key_status.setFont(QFont("Consolas", 9))
        self._key_status.setStyleSheet(f"color: {C.MUTED}; border: none;")
        kl.addWidget(self._key_status)
        layout.addWidget(key_card)

        # Load saved key
        self._load_key()

        layout.addStretch()
        return page

    # ── STATUS BAR ──
    def _build_statusbar(self, parent_layout):
        sb = QFrame()
        sb.setFixedHeight(36)
        sb.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.PANEL2}, stop:0.5 {C.PANEL}, stop:1 {C.PANEL2});
                border-top: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.CYAN}, stop:0.5 {C.PINK}, stop:1 {C.PURPLE});
            }}
        """)
        sbl = QHBoxLayout(sb)
        sbl.setContentsMargins(12, 0, 12, 0)
        st = QLabel(T("status"))
        st.setFont(QFont("Consolas", 8, QFont.Bold))
        st.setStyleSheet(f"color: {C.PINK};")
        sbl.addWidget(st)
        self._status_label = QLabel(T("ready"))
        self._status_label.setFont(QFont("Consolas", 10))
        self._status_label.setStyleSheet(f"color: {C.CYAN};")
        sbl.addWidget(self._status_label)
        sbl.addStretch()
        parent_layout.addWidget(sb)

    # ═══════════════════════════════════════════════════
    #  ACTIONS
    # ═══════════════════════════════════════════════════
    def _switch_tab(self, key):
        pages = {"clean": 0, "opt": 1, "browser": 2, "custom": 3, "settings": 4}
        self._stack.setCurrentIndex(pages.get(key, 0))
        for k, btn in self._sidebar_btns.items():
            btn.set_active(k == key)
        self._rebuild_actions(key)

    def _rebuild_actions(self, tab):
        # Clear old
        while self._action_container.count():
            w = self._action_container.takeAt(0).widget()
            if w:
                w.deleteLater()

        if tab == "clean":
            actions = [
                (T("quick_audit"), C.GREEN, True, lambda: self._start_scan("audit")),
                (T("largest_folders"), C.CYAN, False, lambda: self._start_scan("largefolders")),
                (T("phantom_progs"), C.RED, False, lambda: self._start_scan("phantoms")),
                (T("orphan_folders"), C.CYAN, False, lambda: self._start_scan("orphans")),
                (T("large_files"), C.CYAN, False, lambda: self._start_scan("largefiles")),
                (T("installed_progs"), C.PINK, False, lambda: self._start_scan("installed")),
                (T("junk_temp"), C.ORANGE, False, lambda: self._start_scan("junk")),
                (T("recycle_bin"), C.PINK, False, lambda: self._start_scan("recyclebin")),
                (T("hiberfil"), C.YELLOW, False, lambda: self._start_scan("hibernation")),
            ]
        elif tab == "opt":
            actions = [
                (T("open_opt_tab"), C.ORANGE, True, lambda: None),
            ]
        else:
            actions = []

        for text, color, bold, callback in actions:
            btn = QPushButton(text)
            btn.setFont(QFont("Consolas", 9, QFont.Bold if bold else QFont.Normal))
            btn.setCursor(Qt.PointingHandCursor)
            if bold:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 {color}, stop:1 rgba(0,0,0,0.1));
                        color: {C.BG}; border: none;
                        border-radius: 10px; padding: 10px 10px; text-align: left;
                    }}
                    QPushButton:hover {{
                        background: {color};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {C.PANEL2}; color: {color};
                        border: 1px solid rgba(42,54,96,0.5);
                        border-radius: 10px; padding: 8px 10px; text-align: left;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 {color}, stop:1 rgba(0,0,0,0.2));
                        color: {C.BG}; border-color: {color};
                    }}
                """)
            btn.clicked.connect(callback)
            self._action_container.addWidget(btn)

    def _start_scan(self, scan_type, extra=None):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(2000)

        self._scan_items.clear()
        self._tree.clear()
        self._log_text.clear()
        self._progress.setValue(0)
        self._result_info.setText("")
        self._rec_text.setText(T("scanning"))
        self._btn_delete.setEnabled(False)
        self._sel_label.setText(T("scanning"))

        drive = self._drive_combo.currentText()
        self._worker = ScanWorker(scan_type, drive, extra)
        self._worker.progress.connect(self._on_progress)
        self._worker.item_found.connect(self._on_item_found)
        self._worker.log_msg.connect(self._on_log)
        self._worker.finished_scan.connect(self._on_scan_done)
        self._worker.start()

        self._status_label.setText(T("scanning_t", t=scan_type))
        self._status_label.setStyleSheet(f"color: {C.CYAN};")

        # Switch to clean page to show results
        if scan_type not in ("custom",):
            self._switch_tab("clean")

    def _on_progress(self, pct, status):
        self._progress.setValue(pct)
        self._status_label.setText(status)

    def _on_item_found(self, item: ScanItem):
        self._scan_items.append(item)
        idx = len(self._scan_items)
        tw = QTreeWidgetItem([
            str(idx),
            format_size(item.size),
            item.path,
            item.details,
        ])
        tw.setData(1, Qt.UserRole, item.size)  # For sorting
        # Color by type
        colors = {
            "junk": C.ORANGE, "phantom": C.RED, "hibernation": C.YELLOW,
            "recyclebin": C.PINK, "orphan": C.CYAN, "browser": C.PURPLE,
            "installed": C.TEXT, "folder": C.TEXT, "file": C.DIM,
        }
        c = QColor(colors.get(item.item_type, C.TEXT))
        for col in range(4):
            tw.setForeground(col, c)
        self._tree.addTopLevelItem(tw)

    def _on_log(self, msg):
        self._log_text.append(msg)

    def _on_scan_done(self, recommendation):
        self._progress.setValue(100)
        self._rec_text.setText(recommendation)
        self._status_label.setText(T("done"))
        self._status_label.setStyleSheet(f"color: {C.GREEN};")
        self._result_info.setText(T("items_found", n=len(self._scan_items)))
        total_sz = sum(i.size for i in self._scan_items)
        if total_sz > 0:
            self._result_info.setText(T("items_size", n=len(self._scan_items), sz=format_size(total_sz)))

    def _on_selection_changed(self):
        sel = self._tree.selectedItems()
        n = len(sel)
        if n == 0:
            self._sel_label.setText(T("nothing_sel"))
            self._btn_delete.setEnabled(False)
        else:
            total = sum(self._scan_items[int(it.text(0)) - 1].size for it in sel if int(it.text(0)) - 1 < len(self._scan_items))
            self._sel_label.setText(T("sel_items", n=n, sz=format_size(total)))
            self._btn_delete.setEnabled(True)

    def _select_all(self):
        self._tree.selectAll()

    def _open_in_explorer(self):
        sel = self._tree.selectedItems()
        if sel:
            idx = int(sel[0].text(0)) - 1
            if idx < len(self._scan_items):
                path = self._scan_items[idx].path
                if os.path.exists(path):
                    if os.path.isdir(path):
                        os.startfile(path)
                    else:
                        subprocess.Popen(f'explorer /select,"{path}"')

    def _delete_selected(self):
        sel = self._tree.selectedItems()
        if not sel:
            return
        n = len(sel)
        r = QMessageBox.question(self, T("confirm_del_t"),
                                 T("confirm_del_m", n=n),
                                 QMessageBox.Yes | QMessageBox.No)
        if r != QMessageBox.Yes:
            return

        ok, fail, freed = 0, 0, 0
        for it in sel:
            idx = int(it.text(0)) - 1
            if idx >= len(self._scan_items):
                continue
            item = self._scan_items[idx]
            try:
                if item.item_type == "phantom" and item.extra:
                    # Delete registry key
                    parts = item.extra.split("\\")
                    if "WOW6432Node" in item.extra:
                        hkey = winreg.HKEY_LOCAL_MACHINE
                        subpath = "\\".join(parts[:-1]).replace("SOFTWARE\\WOW6432Node\\", "SOFTWARE\\WOW6432Node\\")
                    elif "HKCU" in item.extra or "HKEY_CURRENT_USER" in item.extra:
                        hkey = winreg.HKEY_CURRENT_USER
                        subpath = "\\".join(parts[:-1])
                    else:
                        hkey = winreg.HKEY_LOCAL_MACHINE
                        subpath = "\\".join(parts[:-1])
                    key_name = parts[-1]
                    try:
                        parent = winreg.OpenKey(hkey, subpath.split("\\", 1)[-1] if "\\" in subpath else subpath, 0, winreg.KEY_ALL_ACCESS)
                        winreg.DeleteKey(parent, key_name)
                        winreg.CloseKey(parent)
                        ok += 1
                        freed += item.size
                    except Exception:
                        fail += 1
                elif item.item_type == "recyclebin":
                    subprocess.run(["powershell", "-NoProfile", "-Command",
                                    "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                                   capture_output=True, timeout=30)
                    ok += 1
                    freed += item.size
                elif item.item_type == "hibernation":
                    subprocess.run(["powercfg", "/h", "off"], capture_output=True, timeout=15)
                    ok += 1
                    freed += item.size
                elif item.item_type == "installed" and item.extra:
                    # Run uninstaller
                    subprocess.Popen(item.extra, shell=True)
                    ok += 1
                elif os.path.isdir(item.path):
                    shutil.rmtree(item.path, ignore_errors=True)
                    ok += 1
                    freed += item.size
                elif os.path.isfile(item.path):
                    os.remove(item.path)
                    ok += 1
                    freed += item.size
                else:
                    fail += 1
            except Exception as e:
                self._on_log(f"DELETE FAIL: {item.path} — {e}")
                fail += 1

        QMessageBox.information(self, T("result_title"),
                                T("result_msg", ok=ok, fail=fail, freed=format_size(freed)))
        self._update_disk_info()

    # ── OPTIMIZATION ──
    def _apply_opt(self, checks, title):
        checked = [cb for cb in checks if cb.isChecked()]
        if not checked:
            return
        r = QMessageBox.question(self, T("confirm_title"),
                                 T("confirm_opt", n=len(checked), title=title),
                                 QMessageBox.Yes | QMessageBox.No)
        if r != QMessageBox.Yes:
            return
        ok, fail = 0, 0
        for cb in checked:
            cmd = cb.property("cmd")
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                cb.setStyleSheet(f"color: {C.GREEN}; border: none; spacing: 8px;")
                ok += 1
            except Exception:
                cb.setStyleSheet(f"color: {C.RED}; border: none; spacing: 8px;")
                fail += 1
        QMessageBox.information(self, T("opt_done_t"),
                                T("opt_done_m", ok=ok, fail=fail))

    # ── CUSTOM SCAN ──
    def _pick_custom_folder(self):
        d = QFileDialog.getExistingDirectory(self, T("select_folder"))
        if d:
            self._custom_path.setText(d)

    # ── DISK INFO ──
    def _update_disk_info(self):
        drive = self._drive_combo.currentText()
        try:
            total, used, free = shutil.disk_usage(drive + "\\")
            self._stat_total.set_value(f"{total / 1024**3:.1f} GB")
            self._stat_used.set_value(f"{used / 1024**3:.1f} GB")
            pct_free = (free / total) * 100
            self._stat_free.set_value(f"{free / 1024**3:.1f} GB ({pct_free:.1f}%)")
            if pct_free < 10:
                self._stat_free.set_color(C.RED)
            elif pct_free < 20:
                self._stat_free.set_color(C.ORANGE)
            else:
                self._stat_free.set_color(C.GREEN)
        except Exception:
            pass

    def _on_drive_changed(self, text):
        self._update_disk_info()

    # ── KEY ACTIVATION ──
    def _activate_key(self):
        key = self._key_input.text().strip()
        if not key:
            return
        # Simple validation — try GitHub gist or local check
        # For now accept any properly formatted key
        if len(key.replace("-", "")) >= 20:
            self._key_status.setText(f"{T('key_active')} {key[:10]}...")
            self._key_status.setStyleSheet(f"color: {C.GREEN}; border: none;")
            self._save_key(key)
        else:
            self._key_status.setText(T("key_invalid"))
            self._key_status.setStyleSheet(f"color: {C.RED}; border: none;")

    def _save_key(self, key):
        cfg = os.path.join(app_dir(), "config.json")
        try:
            data = {}
            if os.path.exists(cfg):
                with open(cfg, "r") as f:
                    data = json.load(f)
            data["key"] = key
            with open(cfg, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _load_key(self):
        cfg = os.path.join(app_dir(), "config.json")
        try:
            if os.path.exists(cfg):
                with open(cfg, "r") as f:
                    data = json.load(f)
                key = data.get("key", "")
                if key:
                    self._key_input.setText(key)
                    self._key_status.setText(f"{T('key_active')} {key[:10]}...")
                    self._key_status.setStyleSheet(f"color: {C.GREEN}; border: none;")
        except Exception:
            pass

    # ── AUTO-UPDATER ──
    _update_result = Signal(str)  # "" = up to date, else version

    def _check_update(self):
        self._status_label.setText(T("checking_upd"))
        self._status_label.setStyleSheet(f"color: {C.CYAN};")

        try:
            self._update_result.disconnect()
        except Exception:
            pass
        self._update_result.connect(self._on_update_result)

        def _thread():
            try:
                req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "s0meClean"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode())
                remote = data.get("tag_name", "").lstrip("v")
                if remote and remote != VERSION:
                    self._update_result.emit(remote)
                    return
            except Exception:
                pass
            self._update_result.emit("")

        threading.Thread(target=_thread, daemon=True).start()

    def _on_update_result(self, ver):
        if ver:
            r = QMessageBox.question(self, T("upd_available_t"),
                                     T("upd_available_m", ver=ver, cur=VERSION),
                                     QMessageBox.Yes | QMessageBox.No)
            if r == QMessageBox.Yes:
                self._apply_update()
        else:
            self._status_label.setText(f"{T('up_to_date')} (v{VERSION})")
            self._status_label.setStyleSheet(f"color: {C.GREEN};")

    def _apply_update(self):
        self._status_label.setText(T("downloading"))
        self._status_label.setStyleSheet(f"color: {C.ORANGE};")

        def _download():
            try:
                import tempfile
                tmp = tempfile.mkdtemp()
                zip_path = os.path.join(tmp, "update.zip")
                urllib.request.urlretrieve(UPDATE_URL, zip_path)
                with zipfile.ZipFile(zip_path, "r") as z:
                    z.extractall(tmp)
                os.remove(zip_path)

                # Handle wrapper folder
                src_dir = tmp
                children = os.listdir(tmp)
                if len(children) == 1:
                    candidate = os.path.join(tmp, children[0])
                    if os.path.isdir(candidate):
                        src_dir = candidate

                target = app_dir()
                for item in os.listdir(src_dir):
                    s = os.path.join(src_dir, item)
                    d = os.path.join(target, item)
                    try:
                        if os.path.isdir(s):
                            if os.path.exists(d):
                                shutil.rmtree(d, ignore_errors=True)
                            shutil.copytree(s, d)
                        else:
                            shutil.copy2(s, d)
                    except Exception:
                        pass
                shutil.rmtree(tmp, ignore_errors=True)
                return True
            except Exception:
                return False

        def _done(success):
            if success:
                QMessageBox.information(self, T("updated_t"), T("updated_m"))
                self._status_label.setText(T("upd_installed"))
                self._status_label.setStyleSheet(f"color: {C.GREEN};")
            else:
                self._status_label.setText(T("upd_failed"))
                self._status_label.setStyleSheet(f"color: {C.RED};")

        def _thread():
            ok = _download()
            QTimer.singleShot(0, lambda: _done(ok))

        threading.Thread(target=_thread, daemon=True).start()

    # ── LANGUAGE SWITCH ──
    def _on_lang_changed(self, index):
        new_lang = self._lang_combo.itemData(index)
        if new_lang and new_lang != LANG:
            cfg = os.path.join(app_dir(), "config.json")
            try:
                data = {}
                if os.path.exists(cfg):
                    with open(cfg, "r", encoding="utf-8") as f:
                        data = json.load(f)
                data["language"] = new_lang
                with open(cfg, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
            self._lang_hint.setVisible(True)

    # ── Resize background ──
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg"):
            self._bg.setGeometry(0, 0, self.width(), self.height())


# ═══════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════
def main():
    if not is_admin():
        run_as_admin()

    _load_language()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(C.BG))
    palette.setColor(QPalette.WindowText, QColor(C.TEXT))
    palette.setColor(QPalette.Base, QColor(C.PANEL))
    palette.setColor(QPalette.AlternateBase, QColor(C.PANEL2))
    palette.setColor(QPalette.Text, QColor(C.TEXT))
    palette.setColor(QPalette.Button, QColor(C.PANEL2))
    palette.setColor(QPalette.ButtonText, QColor(C.TEXT))
    palette.setColor(QPalette.Highlight, QColor(C.CYAN))
    palette.setColor(QPalette.HighlightedText, QColor(C.BG))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
