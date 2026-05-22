# -*- coding: utf-8 -*-
"""
s0meClean? — System Optimization Suite
PySide6 GUI  ·  v2.0.0  ·  MIT License  ·  solevoyq

Modules: Cleaner · Game Boost · Monitor · Security · Drivers · Tweaks · Plugins
"""

import ctypes, json, os, platform, shutil, subprocess, sys, threading, time, traceback
import urllib.request, zipfile, winreg, locale, struct
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

VERSION = "2.0.0"
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
    QSlider, QPlainTextEdit, QTabWidget, QTableWidget, QTableWidgetItem,
)
from PySide6.QtCore import (
    Qt, QTimer, Signal, QThread, QPropertyAnimation, QEasingCurve,
    QUrl, QSize, QPoint, QRect, QParallelAnimationGroup,
    QSequentialAnimationGroup, Property,
)
from PySide6.QtGui import (
    QFont, QColor, QPalette, QPainter, QLinearGradient, QRadialGradient,
    QPen, QBrush, QIcon, QPixmap, QFontDatabase, QDesktopServices,
    QPainterPath, QConicalGradient, QSyntaxHighlighter, QTextCharFormat,
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
    "subtitle":       {"EN": "// SYSTEM OPTIMIZATION SUITE",    "RU": "// СИСТЕМНАЯ ОПТИМИЗАЦИЯ"},
    "drive":          {"EN": "DRIVE",                         "RU": "ДИСК"},
    "total":          {"EN": "TOTAL",                         "RU": "ВСЕГО"},
    "used":           {"EN": "USED",                          "RU": "ЗАНЯТО"},
    "free":           {"EN": "FREE",                          "RU": "СВОБОДНО"},
    "admin_yes":      {"EN": "● ADMIN",                       "RU": "● АДМИН"},
    "admin_no":       {"EN": "● NO ADMIN",                    "RU": "● НЕТ ПРАВ"},

    # Sidebar tabs
    "tab_clean":      {"EN": "CLEANER",                       "RU": "ОЧИСТКА"},
    "tab_boost":      {"EN": "BOOST",                         "RU": "УСКОРЕНИЕ"},
    "tab_monitor":    {"EN": "MONITOR",                       "RU": "МОНИТОР"},
    "tab_security":   {"EN": "SECURITY",                      "RU": "ЗАЩИТА"},
    "tab_drivers":    {"EN": "DRIVERS",                       "RU": "ДРАЙВЕРЫ"},
    "tab_tweaks":     {"EN": "TWEAKS",                        "RU": "ТВИКИ"},
    "tab_plugins":    {"EN": "PLUGINS",                       "RU": "ПЛАГИНЫ"},
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
    "browser_cache":  {"EN": "🌐 Browser caches",            "RU": "🌐 Кэш браузеров"},

    # Boost page
    "boost_title":    {"EN": "// GAME BOOST",                 "RU": "// УСКОРЕНИЕ ИГР"},
    "boost_desc":     {"EN": "Optimize your system for maximum gaming performance.",
                       "RU": "Оптимизируйте систему для максимальной игровой производительности."},
    "boost_enable":   {"EN": "🚀  ENABLE GAME MODE",          "RU": "🚀  ВКЛЮЧИТЬ ИГРОВОЙ РЕЖИМ"},
    "boost_disable":  {"EN": "⏹  DISABLE GAME MODE",          "RU": "⏹  ОТКЛЮЧИТЬ ИГРОВОЙ РЕЖИМ"},
    "boost_active":   {"EN": "GAME MODE ACTIVE",              "RU": "ИГРОВОЙ РЕЖИМ АКТИВЕН"},
    "boost_inactive": {"EN": "GAME MODE INACTIVE",            "RU": "ИГРОВОЙ РЕЖИМ НЕАКТИВЕН"},
    "boost_priority": {"EN": "Set process priority to High",  "RU": "Установить приоритет процесса на Высокий"},
    "boost_services": {"EN": "Disable background services",   "RU": "Отключить фоновые службы"},
    "boost_ram":      {"EN": "Clean RAM (soft)",              "RU": "Очистить RAM (мягкая)"},
    "boost_anim":     {"EN": "Disable Windows animations",    "RU": "Отключить анимации Windows"},
    "boost_power":    {"EN": "High Performance power plan",   "RU": "Схема питания: Высокая производительность"},
    "boost_nagle":    {"EN": "Disable Nagle's algorithm",     "RU": "Отключить алгоритм Nagle"},
    "boost_overlay":  {"EN": "Show performance overlay",      "RU": "Показывать оверлей производительности"},
    "boost_applied":  {"EN": "Game Mode applied: {n} tweaks", "RU": "Игровой режим применён: {n} твиков"},
    "boost_restored": {"EN": "Game Mode disabled. Settings restored.", "RU": "Игровой режим отключён. Настройки восстановлены."},
    "boost_stats":    {"EN": "// CURRENT PERFORMANCE",        "RU": "// ТЕКУЩАЯ ПРОИЗВОДИТЕЛЬНОСТЬ"},

    # Monitor page
    "mon_title":      {"EN": "// SYSTEM MONITOR",             "RU": "// СИСТЕМНЫЙ МОНИТОР"},
    "mon_cpu":        {"EN": "CPU",                           "RU": "ЦПУ"},
    "mon_ram":        {"EN": "RAM",                           "RU": "ОЗУ"},
    "mon_disk":       {"EN": "DISK I/O",                      "RU": "ДИСК I/O"},
    "mon_net":        {"EN": "NETWORK",                       "RU": "СЕТЬ"},
    "mon_procs":      {"EN": "// PROCESSES",                  "RU": "// ПРОЦЕССЫ"},
    "mon_kill":       {"EN": "KILL PROCESS",                  "RU": "ЗАВЕРШИТЬ ПРОЦЕСС"},
    "mon_refresh":    {"EN": "REFRESH",                       "RU": "ОБНОВИТЬ"},
    "mon_name":       {"EN": "NAME",                          "RU": "ИМЯ"},
    "mon_pid":        {"EN": "PID",                           "RU": "PID"},
    "mon_cpu_col":    {"EN": "CPU %",                         "RU": "ЦПУ %"},
    "mon_ram_col":    {"EN": "RAM",                           "RU": "ОЗУ"},
    "mon_no_psutil":  {"EN": "Install psutil for monitoring: pip install psutil",
                       "RU": "Установите psutil для мониторинга: pip install psutil"},

    # Security page
    "sec_title":      {"EN": "// SECURITY CHECK",             "RU": "// ПРОВЕРКА БЕЗОПАСНОСТИ"},
    "sec_desc":       {"EN": "Check startup apps and suspicious processes.",
                       "RU": "Проверка автозагрузки и подозрительных процессов."},
    "sec_startup":    {"EN": "// STARTUP APPS",               "RU": "// АВТОЗАГРУЗКА"},
    "sec_suspicious": {"EN": "// SUSPICIOUS PROCESSES",       "RU": "// ПОДОЗРИТЕЛЬНЫЕ ПРОЦЕССЫ"},
    "sec_scan":       {"EN": "🔍  SCAN SECURITY",              "RU": "🔍  СКАНИРОВАТЬ"},
    "sec_safe":       {"EN": "🟢  SYSTEM SAFE",                "RU": "🟢  СИСТЕМА БЕЗОПАСНА"},
    "sec_warning":    {"EN": "🟡  WARNINGS FOUND",             "RU": "🟡  НАЙДЕНЫ ПРЕДУПРЕЖДЕНИЯ"},
    "sec_risk":       {"EN": "🔴  RISKS DETECTED",             "RU": "🔴  ОБНАРУЖЕНЫ РИСКИ"},
    "sec_disable":    {"EN": "DISABLE",                       "RU": "ОТКЛЮЧИТЬ"},
    "sec_location":   {"EN": "LOCATION",                      "RU": "РАСПОЛОЖЕНИЕ"},
    "sec_status":     {"EN": "STATUS",                        "RU": "СТАТУС"},

    # Drivers page
    "drv_title":      {"EN": "// DRIVER CHECKER",             "RU": "// ПРОВЕРКА ДРАЙВЕРОВ"},
    "drv_desc":       {"EN": "Check installed drivers and their versions.",
                       "RU": "Проверка установленных драйверов и их версий."},
    "drv_scan":       {"EN": "🔍  CHECK DRIVERS",              "RU": "🔍  ПРОВЕРИТЬ ДРАЙВЕРЫ"},
    "drv_device":     {"EN": "DEVICE",                        "RU": "УСТРОЙСТВО"},
    "drv_version":    {"EN": "VERSION",                       "RU": "ВЕРСИЯ"},
    "drv_date":       {"EN": "DATE",                          "RU": "ДАТА"},
    "drv_status_col": {"EN": "STATUS",                        "RU": "СТАТУС"},
    "drv_ok":         {"EN": "OK",                            "RU": "ОК"},
    "drv_update":     {"EN": "Update Available",              "RU": "Доступно обновление"},

    # Tweaks page
    "twk_title":      {"EN": "// SYSTEM TWEAKS",              "RU": "// СИСТЕМНЫЕ ТВИКИ"},
    "twk_desc":       {"EN": "Toggle system optimizations. Changes apply immediately.",
                       "RU": "Переключайте оптимизации системы. Изменения применяются сразу."},
    "twk_telemetry":  {"EN": "Disable Windows Telemetry",     "RU": "Отключить телеметрию Windows"},
    "twk_telemetry_d": {"EN": "Stop sending diagnostic data to Microsoft",
                        "RU": "Прекратить отправку диагностических данных в Microsoft"},
    "twk_cortana":    {"EN": "Disable Cortana",               "RU": "Отключить Cortana"},
    "twk_cortana_d":  {"EN": "Turn off Cortana voice assistant",
                       "RU": "Выключить голосовой помощник Cortana"},
    "twk_ads":        {"EN": "Disable Advertising ID",        "RU": "Отключить рекламный ID"},
    "twk_ads_d":      {"EN": "Stop personalized ads across apps",
                       "RU": "Остановить персонализированную рекламу"},
    "twk_tips":       {"EN": "Disable Tips & Suggestions",    "RU": "Отключить советы и предложения"},
    "twk_tips_d":     {"EN": "Remove notification tips from Windows",
                       "RU": "Убрать уведомления с советами от Windows"},
    "twk_fastboot":   {"EN": "Enable Fast Startup",           "RU": "Включить быстрый запуск"},
    "twk_fastboot_d": {"EN": "Reduce boot time using hibernation trick",
                       "RU": "Уменьшить время загрузки через гибернацию"},
    "twk_visual":     {"EN": "Performance Visual Effects",    "RU": "Визуальные эффекты: Производительность"},
    "twk_visual_d":   {"EN": "Disable animations for faster UI",
                       "RU": "Отключить анимации для быстрого интерфейса"},
    "twk_sysmain":    {"EN": "Disable SysMain (Superfetch)",  "RU": "Отключить SysMain (Superfetch)"},
    "twk_sysmain_d":  {"EN": "Reduce disk usage on HDD systems",
                       "RU": "Уменьшить нагрузку на диск (для HDD)"},
    "twk_wsearch":    {"EN": "Disable Windows Search Index",  "RU": "Отключить индексацию поиска"},
    "twk_wsearch_d":  {"EN": "Stop background file indexing",
                       "RU": "Остановить фоновую индексацию файлов"},
    "twk_hibernate":  {"EN": "Disable Hibernation (~6 GB)",   "RU": "Отключить гибернацию (~6 ГБ)"},
    "twk_hibernate_d": {"EN": "Remove hiberfil.sys and free disk space",
                        "RU": "Удалить hiberfil.sys и освободить место на диске"},
    "twk_network":    {"EN": "Optimize Network Settings",     "RU": "Оптимизировать сетевые настройки"},
    "twk_network_d":  {"EN": "Disable Nagle, optimize TCP/IP settings",
                       "RU": "Отключить Nagle, оптимизировать TCP/IP"},
    "twk_fastshut":   {"EN": "Faster Shutdown",               "RU": "Быстрое выключение"},
    "twk_fastshut_d": {"EN": "Reduce shutdown waiting time",
                       "RU": "Уменьшить время ожидания при выключении"},
    "twk_gamemode":   {"EN": "Windows Game Mode",             "RU": "Игровой режим Windows"},
    "twk_gamemode_d": {"EN": "Enable built-in Windows game optimization",
                       "RU": "Включить встроенную игровую оптимизацию Windows"},
    "twk_on":         {"EN": "ON",                            "RU": "ВКЛ"},
    "twk_off":        {"EN": "OFF",                           "RU": "ВЫКЛ"},
    "twk_applied":    {"EN": "Tweak applied!",                "RU": "Твик применён!"},
    "twk_error":      {"EN": "Failed to apply",               "RU": "Ошибка применения"},
    "twk_quick":      {"EN": "// QUICK ACTIONS",              "RU": "// БЫСТРЫЕ ДЕЙСТВИЯ"},

    # Plugins page
    "plg_title":      {"EN": "// PLUGINS & SCRIPTS",          "RU": "// ПЛАГИНЫ И СКРИПТЫ"},
    "plg_desc":       {"EN": "Write and run custom Python scripts. Access system info via the API.",
                       "RU": "Пишите и запускайте Python скрипты. Доступ к системной информации через API."},
    "plg_run":        {"EN": "▶  RUN",                         "RU": "▶  ЗАПУСК"},
    "plg_clear":      {"EN": "CLEAR",                         "RU": "ОЧИСТИТЬ"},
    "plg_output":     {"EN": "// OUTPUT",                     "RU": "// ВЫВОД"},
    "plg_editor":     {"EN": "// SCRIPT EDITOR",              "RU": "// РЕДАКТОР СКРИПТОВ"},
    "plg_templates":  {"EN": "TEMPLATES",                     "RU": "ШАБЛОНЫ"},
    "plg_sysinfo":    {"EN": "System Info",                   "RU": "Информация о системе"},
    "plg_proclist":   {"EN": "Process List",                  "RU": "Список процессов"},
    "plg_diskinfo":   {"EN": "Disk Info",                     "RU": "Информация о дисках"},
    "plg_netinfo":    {"EN": "Network Info",                  "RU": "Информация о сети"},
    "plg_running":    {"EN": "Running script...",             "RU": "Выполнение скрипта..."},
    "plg_done":       {"EN": "Script finished.",              "RU": "Скрипт завершён."},

    # Settings page
    "settings_title": {"EN": "// SETTINGS",                   "RU": "// НАСТРОЙКИ"},
    "about":          {"EN": "ABOUT",                         "RU": "О ПРОГРАММЕ"},
    "about_text":     {"EN": "s0meClean? — System Optimization Suite.\n"
                             "Cleaner · Game Boost · Monitor · Security · Drivers · Tweaks · Plugins\n"
                             "Open source, MIT License. by solevoyq",
                       "RU": "s0meClean? — Комплекс оптимизации системы.\n"
                             "Очистка · Ускорение · Монитор · Защита · Драйверы · Твики · Плагины\n"
                             "Открытый код, лицензия MIT. by solevoyq"},
    "access_key":     {"EN": "ACCESS KEY",                    "RU": "КЛЮЧ ДОСТУПА"},
    "activate":       {"EN": "ACTIVATE",                      "RU": "АКТИВИРОВАТЬ"},
    "key_none":       {"EN": "STATUS: Not activated",         "RU": "СТАТУС: Не активирован"},
    "key_active":     {"EN": "STATUS: ACTIVE  ·  Key:",       "RU": "СТАТУС: АКТИВЕН  ·  Ключ:"},
    "key_invalid":    {"EN": "STATUS: Invalid key format",    "RU": "СТАТУС: Неверный формат ключа"},
    "language":       {"EN": "LANGUAGE",                      "RU": "ЯЗЫК"},
    "lang_restart":   {"EN": "Language will change after restart.",
                       "RU": "Язык изменится после перезапуска."},
    "theme_label":    {"EN": "THEME",                         "RU": "ТЕМА"},

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

    # Scan worker results
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

    # Overlay
    "overlay_title":  {"EN": "PERFORMANCE OVERLAY",           "RU": "ОВЕРЛЕЙ ПРОИЗВОДИТЕЛЬНОСТИ"},
    "overlay_opacity": {"EN": "Opacity",                      "RU": "Прозрачность"},
    "overlay_size":   {"EN": "Size",                          "RU": "Размер"},

    # Custom scan
    "custom_title":   {"EN": "// CUSTOM SCAN",                "RU": "// СВОЙ СКАН"},
    "custom_desc":    {"EN": "Pick a folder — shows largest subfolders and files inside.",
                       "RU": "Выберите папку — покажет крупнейшие подпапки и файлы внутри."},
    "path_label":     {"EN": "Path:",                         "RU": "Путь:"},
    "pick_folder":    {"EN": "PICK FOLDER",                   "RU": "ВЫБРАТЬ ПАПКУ"},
    "scan_go":        {"EN": "SCAN  ▶",                       "RU": "СКАН  ▶"},
    "custom_hint":    {"EN": "Results will appear after scan.",
                       "RU": "Результаты появятся после скана."},

    # Notifications
    "notif_high_cpu": {"EN": "⚠ High CPU usage: {v}%",       "RU": "⚠ Высокая нагрузка ЦПУ: {v}%"},
    "notif_low_disk": {"EN": "⚠ Low disk space: {v}",        "RU": "⚠ Мало места на диске: {v}"},
    "notif_high_ram": {"EN": "⚠ High RAM usage: {v}%",       "RU": "⚠ Высокое использование ОЗУ: {v}%"},
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
    total = 0
    count = 0
    try:
        for dirpath, _dirnames, filenames in os.walk(path):
            for f in filenames:
                count += 1
                if count > max_files:
                    return total
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
    item_type: str
    extra: str = ""


# ═══════════════════════════════════════════════════
#  SCAN WORKER THREAD
# ═══════════════════════════════════════════════════
class ScanWorker(QThread):
    progress = Signal(int, str)
    item_found = Signal(object)
    log_msg = Signal(str)
    finished_scan = Signal(str)

    def __init__(self, scan_type: str, drive: str = "C:", extra=None):
        super().__init__()
        self.scan_type = scan_type
        self.drive = drive
        self.extra = extra
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def _log(self, msg):
        self.log_msg.emit(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def _emit(self, path, size, details, item_type, extra=""):
        self.item_found.emit(ScanItem(path, size, details, item_type, extra))

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
        for idx, (fp, sz, det, tp) in enumerate(items[:100]):
            self._emit(fp, sz, det, tp)
            self.progress.emit(min(100, idx * 100 // max(1, len(items))), os.path.basename(fp))
        self.progress.emit(100, "Done")
        total_sz = sum(s for _, s, _, _ in items[:100])
        self.finished_scan.emit(T("rec_custom", n=len(items[:100]), sz=format_size(total_sz)))

    def _reg_val(self, key, name):
        try:
            return winreg.QueryValueEx(key, name)[0]
        except (OSError, FileNotFoundError):
            return None


# ═══════════════════════════════════════════════════
#  MONITOR WORKER THREAD (psutil-based)
# ═══════════════════════════════════════════════════
class MonitorWorker(QThread):
    stats_update = Signal(dict)

    def __init__(self):
        super().__init__()
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        if not HAS_PSUTIL:
            return
        while self._running:
            try:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                net_io = psutil.net_io_counters()
                self.stats_update.emit({
                    "cpu": cpu,
                    "ram_percent": mem.percent,
                    "ram_used": mem.used,
                    "ram_total": mem.total,
                    "disk_read": disk_io.read_bytes if disk_io else 0,
                    "disk_write": disk_io.write_bytes if disk_io else 0,
                    "net_sent": net_io.bytes_sent if net_io else 0,
                    "net_recv": net_io.bytes_recv if net_io else 0,
                })
            except Exception:
                pass


# ═══════════════════════════════════════════════════
#  ANIMATED BACKGROUND WIDGET
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

        for l in self._lines:
            x = int(l["x"] * w)
            y2 = int(l["len"] * h)
            grad = QLinearGradient(x, 0, x, y2)
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
            p.drawLine(x, 0, x, y2)

        p.setPen(Qt.NoPen)
        for pt in self._particles:
            x = int(pt["x"] * w)
            y = int(pt["y"] * h)
            c = QColor(pt["c"])
            c.setAlphaF(0.4 + 0.3 * math.sin(self._t * 0.05 + x))
            p.setBrush(c)
            p.drawEllipse(QPoint(x, y), int(pt["r"]), int(pt["r"]))
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
        p.setBrush(QColor(C.PANEL2))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, w, h, 4, 4)
        fw = int(w * self._value / 100)
        if fw > 0:
            grad = QLinearGradient(0, 0, fw, 0)
            grad.setColorAt(0, QColor(C.CYAN))
            grad.setColorAt(0.5, QColor(C.PURPLE))
            grad.setColorAt(1, QColor(C.PINK))
            p.setBrush(grad)
            p.drawRoundedRect(0, 0, fw, h, 4, 4)
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
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(40)
        self.setStyleSheet("background: transparent; border: none;")

    def set_active(self, active):
        self._active = active
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        if self._active:
            grad = QLinearGradient(0, 0, w, 0)
            ac = QColor(self._accent)
            ac.setAlphaF(0.18)
            grad.setColorAt(0, ac)
            ac2 = QColor(self._accent)
            ac2.setAlphaF(0.03)
            grad.setColorAt(1, ac2)
            p.setBrush(grad)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(4, 2, w - 8, h - 4, 8, 8)
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
            p.drawRoundedRect(4, 2, w - 8, h - 4, 8, 8)

        p.setFont(QFont("Segoe UI", 12))
        p.setPen(QColor(self._accent if self._active else C.MUTED))
        p.drawText(QRect(12, 0, 28, h), Qt.AlignCenter, self._icon_text)

        f = QFont("Segoe UI", 9)
        f.setBold(self._active)
        f.setLetterSpacing(QFont.AbsoluteSpacing, 0.5 if self._active else 0)
        p.setFont(f)
        p.setPen(QColor(C.TEXT if self._active else C.DIM))
        p.drawText(QRect(42, 0, w - 52, h), Qt.AlignVCenter | Qt.AlignLeft, self._text)
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
        self.setMinimumWidth(130)
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
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(2)
        self._lbl = QLabel(label)
        self._lbl.setFont(QFont("Segoe UI", 7, QFont.Bold))
        self._lbl.setStyleSheet(f"color: {C.MUTED}; border: none; letter-spacing: 2px;")
        self._val = QLabel(value)
        self._val.setFont(QFont("Consolas", 16, QFont.Black))
        self._val.setStyleSheet(f"color: {accent}; border: none;")
        layout.addWidget(self._lbl)
        layout.addWidget(self._val)

    def set_value(self, v):
        self._val.setText(v)

    def set_color(self, c):
        self._val.setStyleSheet(f"color: {c}; border: none;")


# ═══════════════════════════════════════════════════
#  TOGGLE SWITCH
# ═══════════════════════════════════════════════════
class ToggleSwitch(QWidget):
    toggled = Signal(bool)

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 26)
        self._checked = checked
        self._offset = 24 if checked else 2
        self.setCursor(Qt.PointingHandCursor)

    def isChecked(self):
        return self._checked

    def setChecked(self, val):
        self._checked = val
        self._offset = 24 if val else 2
        self.update()

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._offset = 24 if self._checked else 2
        self.update()
        self.toggled.emit(self._checked)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Track
        if self._checked:
            grad = QLinearGradient(0, 0, 50, 0)
            grad.setColorAt(0, QColor(C.CYAN))
            grad.setColorAt(1, QColor(C.PURPLE))
            p.setBrush(grad)
        else:
            p.setBrush(QColor(C.PANEL3))
        p.setPen(QPen(QColor(C.BORDER), 1))
        p.drawRoundedRect(0, 0, 50, 26, 13, 13)

        # Knob
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#ffffff" if self._checked else C.DIM))
        p.drawEllipse(self._offset, 3, 20, 20)
        p.end()


# ═══════════════════════════════════════════════════
#  MINI GRAPH WIDGET (for Monitor)
# ═══════════════════════════════════════════════════
class MiniGraph(QWidget):
    def __init__(self, label="", color=C.CYAN, max_val=100, parent=None):
        super().__init__(parent)
        self._label = label
        self._color = color
        self._max_val = max_val
        self._data = [0.0] * 60
        self._current_text = "0%"
        self.setMinimumHeight(120)
        self.setMinimumWidth(200)

    def add_value(self, v):
        self._data.append(v)
        if len(self._data) > 60:
            self._data = self._data[-60:]
        self.update()

    def set_text(self, t):
        self._current_text = t

    def paintEvent(self, event):
        import math
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        p.setBrush(QColor(C.PANEL))
        p.setPen(QPen(QColor(C.BORDER), 1))
        p.drawRoundedRect(0, 0, w, h, 10, 10)

        # Label
        p.setFont(QFont("Consolas", 8, QFont.Bold))
        p.setPen(QColor(self._color))
        p.drawText(QRect(10, 5, w - 20, 20), Qt.AlignLeft, self._label)

        # Current value
        p.setFont(QFont("Consolas", 14, QFont.Black))
        p.drawText(QRect(10, 5, w - 20, 20), Qt.AlignRight, self._current_text)

        # Graph area
        margin_top = 30
        margin_bottom = 10
        margin_lr = 10
        gw = w - margin_lr * 2
        gh = h - margin_top - margin_bottom

        if gh < 10 or gw < 10:
            p.end()
            return

        # Grid lines
        grid_pen = QPen(QColor(C.BORDER))
        grid_pen.setWidthF(0.5)
        p.setPen(grid_pen)
        for i in range(4):
            y = margin_top + int(gh * i / 3)
            p.drawLine(margin_lr, y, w - margin_lr, y)

        # Data line
        if len(self._data) >= 2:
            path = QPainterPath()
            n = len(self._data)
            for i, v in enumerate(self._data):
                x = margin_lr + (i / (n - 1)) * gw
                y = margin_top + gh - (min(v, self._max_val) / max(self._max_val, 1)) * gh
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)

            # Fill under curve
            fill_path = QPainterPath(path)
            fill_path.lineTo(margin_lr + gw, margin_top + gh)
            fill_path.lineTo(margin_lr, margin_top + gh)
            fill_path.closeSubpath()
            fill_grad = QLinearGradient(0, margin_top, 0, margin_top + gh)
            fc = QColor(self._color)
            fc.setAlphaF(0.15)
            fill_grad.setColorAt(0, fc)
            fc2 = QColor(self._color)
            fc2.setAlphaF(0.02)
            fill_grad.setColorAt(1, fc2)
            p.setPen(Qt.NoPen)
            p.setBrush(fill_grad)
            p.drawPath(fill_path)

            # Line
            line_pen = QPen(QColor(self._color), 2)
            p.setPen(line_pen)
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)

            # Dot at current value
            if self._data:
                last_x = margin_lr + gw
                last_y = margin_top + gh - (min(self._data[-1], self._max_val) / max(self._max_val, 1)) * gh
                p.setPen(Qt.NoPen)
                gc = QColor(self._color)
                gc.setAlphaF(0.3)
                p.setBrush(gc)
                p.drawEllipse(QPoint(int(last_x), int(last_y)), 6, 6)
                p.setBrush(QColor(self._color))
                p.drawEllipse(QPoint(int(last_x), int(last_y)), 3, 3)

        p.end()


# ═══════════════════════════════════════════════════
#  PERFORMANCE OVERLAY WINDOW
# ═══════════════════════════════════════════════════
class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(220, 140)
        self._dragging = False
        self._offset = QPoint()
        self._stats = {"cpu": 0, "ram": 0, "gpu": "N/A", "net": "0 KB/s"}
        self._opacity = 0.85

        # Position top-right
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.width() - 240, 20)

    def set_stats(self, stats):
        self._stats = stats
        self.update()

    def set_opacity(self, val):
        self._opacity = val
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        bg = QColor(C.BG)
        bg.setAlphaF(self._opacity)
        p.setBrush(bg)
        p.setPen(QPen(QColor(C.CYAN), 1))
        p.drawRoundedRect(1, 1, w - 2, h - 2, 12, 12)

        # Header
        p.setFont(QFont("Consolas", 8, QFont.Bold))
        p.setPen(QColor(C.CYAN))
        p.drawText(QRect(12, 8, w - 24, 16), Qt.AlignLeft, "s0meClean? OVERLAY")

        # Stats
        y = 30
        stats_list = [
            ("CPU", f"{self._stats.get('cpu', 0):.0f}%", C.CYAN),
            ("RAM", f"{self._stats.get('ram', 0):.0f}%", C.PURPLE),
            ("GPU", str(self._stats.get('gpu', 'N/A')), C.GREEN),
            ("NET", str(self._stats.get('net', '0')), C.PINK),
        ]
        for label, value, color in stats_list:
            p.setFont(QFont("Consolas", 9))
            p.setPen(QColor(C.MUTED))
            p.drawText(QRect(12, y, 50, 20), Qt.AlignLeft | Qt.AlignVCenter, label)

            p.setFont(QFont("Consolas", 11, QFont.Bold))
            p.setPen(QColor(color))
            p.drawText(QRect(55, y, w - 70, 20), Qt.AlignLeft | Qt.AlignVCenter, value)

            # Mini bar
            try:
                val = float(value.replace('%', '').replace(' ', '').split('/')[0])
                bar_w = int((w - 80) * min(val, 100) / 100)
                if bar_w > 0:
                    bar_c = QColor(color)
                    bar_c.setAlphaF(0.2)
                    p.setPen(Qt.NoPen)
                    p.setBrush(bar_c)
                    p.drawRoundedRect(55, y + 18, bar_w, 3, 1, 1)
            except (ValueError, IndexError):
                pass

            y += 25

        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._offset)

    def mouseReleaseEvent(self, event):
        self._dragging = False


# ═══════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════
class MainWindow(QMainWindow):
    _update_result = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"s0meClean? v{VERSION}")
        self.setMinimumSize(1300, 800)
        self.resize(1400, 880)
        self._worker = None
        self._scan_items: List[ScanItem] = []
        self._monitor_worker = None
        self._overlay = None
        self._game_mode_active = False
        self._prev_disk_io = None
        self._prev_net_io = None

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet(f"background-color: {C.BG}; color: {C.TEXT};")

        self._bg = CyberBackground(central)
        self._bg.setGeometry(0, 0, 2000, 2000)
        self._bg.lower()

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._build_header(main_layout)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        self._build_sidebar(body)
        self._build_content(body)
        main_layout.addLayout(body, 1)

        self._build_statusbar(main_layout)

        self._switch_tab("clean")
        self._update_disk_info()

        # Start monitor if psutil available
        if HAS_PSUTIL:
            self._start_monitor()

    def closeEvent(self, event):
        if self._monitor_worker:
            self._monitor_worker.stop()
            self._monitor_worker.wait(2000)
        if self._overlay:
            self._overlay.close()
        super().closeEvent(event)

    # ── HEADER ──
    def _build_header(self, parent_layout):
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.PANEL}, stop:0.5 {C.PANEL2}, stop:1 {C.PANEL});
                border-bottom: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.CYAN}, stop:0.5 {C.PINK}, stop:1 {C.PURPLE});
            }}
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 6, 16, 6)

        # Logo
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(1)
        title = QLabel("s0meClean?")
        title.setFont(QFont("Consolas", 20, QFont.Black))
        title.setStyleSheet(f"color: {C.CYAN}; background: transparent;")
        subtitle = QLabel(T("subtitle"))
        subtitle.setFont(QFont("Segoe UI", 8, QFont.Bold))
        subtitle.setStyleSheet(f"color: {C.PINK}; background: transparent; letter-spacing: 2px;")
        logo_layout.addWidget(title)
        logo_layout.addWidget(subtitle)
        hl.addLayout(logo_layout)
        hl.addSpacing(30)

        # Drive selector
        drive_layout = QVBoxLayout()
        dl = QLabel(T("drive"))
        dl.setFont(QFont("Consolas", 7, QFont.Bold))
        dl.setStyleSheet(f"color: {C.MUTED}; background: transparent;")
        self._drive_combo = QComboBox()
        self._drive_combo.setFont(QFont("Consolas", 12, QFont.Bold))
        self._drive_combo.setStyleSheet(f"""
            QComboBox {{
                background: {C.PANEL2}; color: {C.CYAN}; border: 1px solid {C.BORDER};
                border-radius: 6px; padding: 4px 8px; min-width: 60px;
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
        hl.addSpacing(20)

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
        admin_badge.setFont(QFont("Consolas", 9, QFont.Bold))
        admin_badge.setStyleSheet(f"color: {C.GREEN if is_admin() else C.RED}; background: transparent;")
        hl.addWidget(admin_badge)
        hl.addSpacing(8)

        ver_badge = QLabel(f"v{VERSION}")
        ver_badge.setFont(QFont("Consolas", 9))
        ver_badge.setStyleSheet(f"""
            color: {C.CYAN}; background: {C.PANEL2}; border: 1px solid {C.CYAN_D};
            border-radius: 10px; padding: 2px 10px;
        """)
        hl.addWidget(ver_badge)

        parent_layout.addWidget(header)

    # ── SIDEBAR ──
    def _build_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {C.PANEL}, stop:1 {C.BG2});
                border-right: 1px solid {C.BORDER};
            }}
        """)
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(6, 10, 6, 10)
        sl.setSpacing(2)

        self._sidebar_btns = {}
        tabs = [
            ("clean",    T("tab_clean"),    "🧹", C.CYAN),
            ("boost",    T("tab_boost"),    "🚀", C.GREEN),
            ("monitor",  T("tab_monitor"),  "📊", C.PURPLE),
            ("security", T("tab_security"), "🛡", C.ORANGE),
            ("drivers",  T("tab_drivers"),  "🔄", C.CYAN_D),
            ("tweaks",   T("tab_tweaks"),   "⚡", C.YELLOW),
            ("plugins",  T("tab_plugins"),  "🧩", C.PINK),
            ("settings", T("tab_settings"), "⚙", C.DIM),
        ]
        for key, text, icon, color in tabs:
            btn = SidebarButton(text, icon, color)
            btn.clicked.connect(lambda checked=False, k=key: self._switch_tab(k))
            sl.addWidget(btn)
            self._sidebar_btns[key] = btn

        sl.addSpacing(8)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {C.BORDER};")
        sl.addWidget(sep)
        sl.addSpacing(4)

        # Scan actions label
        self._actions_label = QLabel(T("scan_actions"))
        self._actions_label.setFont(QFont("Consolas", 7, QFont.Bold))
        self._actions_label.setStyleSheet(f"color: {C.PINK}; background: transparent;")
        sl.addWidget(self._actions_label)
        sl.addSpacing(2)

        # Action buttons container (scrollable)
        action_scroll = QScrollArea()
        action_scroll.setWidgetResizable(True)
        action_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }"
                                    "QScrollBar:vertical { width: 4px; background: transparent; }"
                                    f"QScrollBar::handle:vertical {{ background: {C.BORDER}; border-radius: 2px; }}"
                                    "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }")
        action_widget = QWidget()
        action_widget.setStyleSheet("background: transparent;")
        self._action_container = QVBoxLayout(action_widget)
        self._action_container.setSpacing(2)
        self._action_container.setContentsMargins(0, 0, 0, 0)
        action_scroll.setWidget(action_widget)
        sl.addWidget(action_scroll, 1)

        sl.addSpacing(4)

        # GitHub button
        gh_btn = QPushButton(T("github_btn"))
        gh_btn.setCursor(Qt.PointingHandCursor)
        gh_btn.setFont(QFont("Segoe UI", 8, QFont.Bold))
        gh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL2}; color: {C.DIM}; border: 1px solid {C.BORDER};
                border-radius: 8px; padding: 8px;
            }}
            QPushButton:hover {{
                color: {C.CYAN}; border-color: {C.CYAN};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0,240,255,0.08), stop:1 {C.PANEL2});
            }}
        """)
        gh_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f"https://github.com/{GITHUB_REPO}")))
        sl.addWidget(gh_btn)

        upd_btn = QPushButton(T("check_updates"))
        upd_btn.setCursor(Qt.PointingHandCursor)
        upd_btn.setFont(QFont("Segoe UI", 8, QFont.Bold))
        upd_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL2}; color: {C.DIM}; border: 1px solid {C.BORDER};
                border-radius: 8px; padding: 8px;
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

        self._page_clean = self._build_clean_page()
        self._page_boost = self._build_boost_page()
        self._page_monitor = self._build_monitor_page()
        self._page_security = self._build_security_page()
        self._page_drivers = self._build_drivers_page()
        self._page_tweaks = self._build_tweaks_page()
        self._page_plugins = self._build_plugins_page()
        self._page_settings = self._build_settings_page()

        self._stack.addWidget(self._page_clean)      # 0
        self._stack.addWidget(self._page_boost)       # 1
        self._stack.addWidget(self._page_monitor)     # 2
        self._stack.addWidget(self._page_security)    # 3
        self._stack.addWidget(self._page_drivers)     # 4
        self._stack.addWidget(self._page_tweaks)      # 5
        self._stack.addWidget(self._page_plugins)     # 6
        self._stack.addWidget(self._page_settings)    # 7

        parent_layout.addWidget(self._stack, 1)

    # ════════════════════════════════════════════════
    #  PAGE: CLEANER
    # ════════════════════════════════════════════════
    def _build_clean_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 10, 16, 8)
        layout.setSpacing(6)

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

        self._progress = NeonProgressBar()
        layout.addWidget(self._progress)

        # Recommendation box
        rec_frame = QFrame()
        rec_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.PANEL}, stop:1 {C.PANEL2});
                border: 1px solid {C.BORDER}; border-radius: 8px;
                border-left: 3px solid {C.PINK};
            }}
        """)
        rec_layout = QVBoxLayout(rec_frame)
        rec_layout.setContentsMargins(12, 6, 12, 6)
        rl = QLabel(T("analysis"))
        rl.setFont(QFont("Consolas", 7, QFont.Bold))
        rl.setStyleSheet(f"color: {C.PINK}; border: none;")
        self._rec_text = QLabel(T("start_hint"))
        self._rec_text.setFont(QFont("Segoe UI", 9))
        self._rec_text.setStyleSheet(f"color: {C.TEXT}; border: none;")
        self._rec_text.setWordWrap(True)
        rec_layout.addWidget(rl)
        rec_layout.addWidget(self._rec_text)
        layout.addWidget(rec_frame)

        # Tree
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["#", T("col_size"), T("col_path"), T("col_type")])
        self._tree.setColumnWidth(0, 50)
        self._tree.setColumnWidth(1, 120)
        self._tree.setColumnWidth(2, 600)
        self._tree.setColumnWidth(3, 200)
        self._tree.setAlternatingRowColors(True)
        self._tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self._tree.setRootIsDecorated(False)
        self._tree.setSortingEnabled(True)
        self._tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {C.PANEL}; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 8px;
                font-family: 'Consolas'; font-size: 10pt;
                alternate-background-color: {C.PANEL2};
                outline: none;
            }}
            QTreeWidget::item {{ padding: 5px 4px; border-bottom: 1px solid rgba(42, 54, 96, 0.4); }}
            QTreeWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0,240,255,0.15), stop:1 rgba(168,85,247,0.08));
                border-left: 3px solid {C.CYAN};
            }}
            QTreeWidget::item:hover {{ background: rgba(0,240,255,0.05); }}
            QHeaderView::section {{
                background: {C.PANEL3}; color: {C.CYAN}; border: none;
                font-family: 'Segoe UI'; font-weight: bold; font-size: 9pt;
                padding: 6px 8px; border-bottom: 2px solid {C.CYAN};
            }}
            QScrollBar:vertical {{ background: {C.PANEL}; width: 6px; border: none; }}
            QScrollBar::handle:vertical {{ background: {C.BORDER}; border-radius: 3px; min-height: 30px; }}
            QScrollBar::handle:vertical:hover {{ background: {C.CYAN_D}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        layout.addWidget(self._tree, 1)

        # Bottom bar
        bottom = QHBoxLayout()
        bottom.setSpacing(10)

        log_frame = QFrame()
        log_frame.setStyleSheet(f"QFrame {{ background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 8px; }}")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(8, 4, 8, 4)
        ll = QLabel(T("activity"))
        ll.setFont(QFont("Consolas", 7, QFont.Bold))
        ll.setStyleSheet(f"color: {C.PINK}; border: none;")
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setFont(QFont("Consolas", 8))
        self._log_text.setStyleSheet(f"color: {C.DIM}; background: transparent; border: none;")
        self._log_text.setMaximumHeight(120)
        log_layout.addWidget(ll)
        log_layout.addWidget(self._log_text)
        bottom.addWidget(log_frame, 3)

        act_frame = QFrame()
        act_frame.setStyleSheet(f"QFrame {{ background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 8px; }}")
        act_layout = QVBoxLayout(act_frame)
        act_layout.setContentsMargins(10, 6, 10, 6)

        self._sel_label = QLabel(T("nothing_sel"))
        self._sel_label.setFont(QFont("Consolas", 8))
        self._sel_label.setStyleSheet(f"color: {C.MUTED}; border: none;")
        act_layout.addWidget(self._sel_label)

        self._btn_delete = QPushButton(T("delete_sel"))
        self._btn_delete.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self._btn_delete.setCursor(Qt.PointingHandCursor)
        self._btn_delete.setStyleSheet(f"""
            QPushButton {{ background: {C.RED}; color: white; border: none; border-radius: 8px; padding: 10px; }}
            QPushButton:hover {{ background: {C.PINK}; }}
            QPushButton:disabled {{ background: {C.PANEL2}; color: {C.MUTED}; }}
        """)
        self._btn_delete.setEnabled(False)
        self._btn_delete.clicked.connect(self._delete_selected)
        act_layout.addWidget(self._btn_delete)

        btn_open = QPushButton(T("open_explorer"))
        btn_open.setFont(QFont("Segoe UI", 8, QFont.Bold))
        btn_open.setCursor(Qt.PointingHandCursor)
        btn_open.setStyleSheet(f"""
            QPushButton {{ background: {C.CYAN}; color: {C.BG}; border: none; border-radius: 8px; padding: 8px; }}
            QPushButton:hover {{ background: {C.CYAN_D}; }}
        """)
        btn_open.clicked.connect(self._open_in_explorer)
        act_layout.addWidget(btn_open)

        btn_sel_all = QPushButton(T("select_all"))
        btn_sel_all.setFont(QFont("Segoe UI", 8, QFont.Bold))
        btn_sel_all.setCursor(Qt.PointingHandCursor)
        btn_sel_all.setStyleSheet(f"""
            QPushButton {{ background: {C.PANEL2}; color: {C.PINK}; border: 1px solid rgba(255,30,130,0.3); border-radius: 8px; padding: 8px; }}
            QPushButton:hover {{ background: {C.PINK}; color: white; }}
        """)
        btn_sel_all.clicked.connect(self._select_all)
        act_layout.addWidget(btn_sel_all)

        bottom.addWidget(act_frame, 2)
        layout.addLayout(bottom)

        self._tree.itemSelectionChanged.connect(self._on_selection_changed)
        return page

    # ════════════════════════════════════════════════
    #  PAGE: GAME BOOST
    # ════════════════════════════════════════════════
    def _build_boost_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)

        t = QLabel(T("boost_title"))
        t.setFont(QFont("Consolas", 16, QFont.Bold))
        t.setStyleSheet(f"color: {C.GREEN};")
        layout.addWidget(t)

        desc = QLabel(T("boost_desc"))
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {C.DIM};")
        layout.addWidget(desc)
        layout.addSpacing(12)

        # Status card
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background: {C.PANEL}; border: 1px solid {C.BORDER};
                border-radius: 12px; border-left: 4px solid {C.GREEN};
            }}
        """)
        sf_l = QHBoxLayout(status_frame)
        sf_l.setContentsMargins(16, 16, 16, 16)
        self._boost_status = QLabel(T("boost_inactive"))
        self._boost_status.setFont(QFont("Consolas", 14, QFont.Bold))
        self._boost_status.setStyleSheet(f"color: {C.MUTED}; border: none;")
        sf_l.addWidget(self._boost_status)
        sf_l.addStretch()
        self._boost_btn = QPushButton(T("boost_enable"))
        self._boost_btn.setFont(QFont("Consolas", 11, QFont.Bold))
        self._boost_btn.setCursor(Qt.PointingHandCursor)
        self._boost_btn.setFixedHeight(44)
        self._boost_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.GREEN}, stop:1 {C.CYAN});
                color: {C.BG}; border: none; border-radius: 10px; padding: 10px 30px;
            }}
            QPushButton:hover {{ background: {C.GREEN}; }}
        """)
        self._boost_btn.clicked.connect(self._toggle_boost)
        sf_l.addWidget(self._boost_btn)
        layout.addWidget(status_frame)
        layout.addSpacing(12)

        # Boost options
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll_w = QWidget()
        scroll_l = QVBoxLayout(scroll_w)
        scroll_l.setSpacing(8)

        self._boost_checks = {}
        boost_options = [
            ("priority", T("boost_priority"), True),
            ("services", T("boost_services"), True),
            ("ram",      T("boost_ram"), True),
            ("anim",     T("boost_anim"), False),
            ("power",    T("boost_power"), True),
            ("nagle",    T("boost_nagle"), False),
            ("overlay",  T("boost_overlay"), True),
        ]
        for key, text, default in boost_options:
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: {C.PANEL}; border: 1px solid {C.BORDER};
                    border-radius: 8px;
                }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 10, 14, 10)
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color: {C.TEXT}; border: none;")
            rl.addWidget(lbl, 1)
            toggle = ToggleSwitch(default)
            rl.addWidget(toggle)
            self._boost_checks[key] = toggle
            scroll_l.addWidget(row)

        # Performance stats
        stats_label = QLabel(T("boost_stats"))
        stats_label.setFont(QFont("Consolas", 10, QFont.Bold))
        stats_label.setStyleSheet(f"color: {C.GREEN};")
        scroll_l.addWidget(stats_label)

        self._boost_stats_frame = QFrame()
        self._boost_stats_frame.setStyleSheet(f"""
            QFrame {{ background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 8px; }}
        """)
        bsf_l = QGridLayout(self._boost_stats_frame)
        bsf_l.setContentsMargins(14, 10, 14, 10)
        self._boost_cpu_label = QLabel("CPU: —")
        self._boost_cpu_label.setFont(QFont("Consolas", 11, QFont.Bold))
        self._boost_cpu_label.setStyleSheet(f"color: {C.CYAN}; border: none;")
        self._boost_ram_label = QLabel("RAM: —")
        self._boost_ram_label.setFont(QFont("Consolas", 11, QFont.Bold))
        self._boost_ram_label.setStyleSheet(f"color: {C.PURPLE}; border: none;")
        bsf_l.addWidget(self._boost_cpu_label, 0, 0)
        bsf_l.addWidget(self._boost_ram_label, 0, 1)
        scroll_l.addWidget(self._boost_stats_frame)

        scroll_l.addStretch()
        scroll.setWidget(scroll_w)
        layout.addWidget(scroll, 1)
        return page

    # ════════════════════════════════════════════════
    #  PAGE: MONITOR
    # ════════════════════════════════════════════════
    def _build_monitor_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 12, 16, 8)
        layout.setSpacing(8)

        t = QLabel(T("mon_title"))
        t.setFont(QFont("Consolas", 14, QFont.Bold))
        t.setStyleSheet(f"color: {C.PURPLE};")
        layout.addWidget(t)

        if not HAS_PSUTIL:
            no_ps = QLabel(T("mon_no_psutil"))
            no_ps.setFont(QFont("Consolas", 11))
            no_ps.setStyleSheet(f"color: {C.RED};")
            layout.addWidget(no_ps)
            layout.addStretch()
            return page

        # Graphs
        graphs = QGridLayout()
        graphs.setSpacing(8)
        self._graph_cpu = MiniGraph(T("mon_cpu"), C.CYAN, 100)
        self._graph_ram = MiniGraph(T("mon_ram"), C.PURPLE, 100)
        self._graph_disk = MiniGraph(T("mon_disk"), C.ORANGE, 100)
        self._graph_net = MiniGraph(T("mon_net"), C.PINK, 100)
        graphs.addWidget(self._graph_cpu, 0, 0)
        graphs.addWidget(self._graph_ram, 0, 1)
        graphs.addWidget(self._graph_disk, 1, 0)
        graphs.addWidget(self._graph_net, 1, 1)
        layout.addLayout(graphs)

        # Process table
        proc_header = QHBoxLayout()
        pl = QLabel(T("mon_procs"))
        pl.setFont(QFont("Consolas", 10, QFont.Bold))
        pl.setStyleSheet(f"color: {C.PINK};")
        proc_header.addWidget(pl)
        proc_header.addStretch()

        kill_btn = QPushButton(T("mon_kill"))
        kill_btn.setFont(QFont("Consolas", 8, QFont.Bold))
        kill_btn.setCursor(Qt.PointingHandCursor)
        kill_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.RED}; color: white; border: none; border-radius: 6px; padding: 6px 14px; }}
            QPushButton:hover {{ background: {C.PINK}; }}
        """)
        kill_btn.clicked.connect(self._kill_process)
        proc_header.addWidget(kill_btn)

        refresh_btn = QPushButton(T("mon_refresh"))
        refresh_btn.setFont(QFont("Consolas", 8, QFont.Bold))
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.CYAN}; color: {C.BG}; border: none; border-radius: 6px; padding: 6px 14px; }}
            QPushButton:hover {{ background: {C.CYAN_D}; }}
        """)
        refresh_btn.clicked.connect(self._refresh_processes)
        proc_header.addWidget(refresh_btn)

        layout.addLayout(proc_header)

        self._proc_table = QTreeWidget()
        self._proc_table.setHeaderLabels([T("mon_name"), T("mon_pid"), T("mon_cpu_col"), T("mon_ram_col")])
        self._proc_table.setColumnWidth(0, 300)
        self._proc_table.setColumnWidth(1, 80)
        self._proc_table.setColumnWidth(2, 80)
        self._proc_table.setColumnWidth(3, 120)
        self._proc_table.setRootIsDecorated(False)
        self._proc_table.setSortingEnabled(True)
        self._proc_table.setAlternatingRowColors(True)
        self._proc_table.setStyleSheet(f"""
            QTreeWidget {{
                background: {C.PANEL}; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 8px;
                font-family: 'Consolas'; font-size: 9pt;
                alternate-background-color: {C.PANEL2}; outline: none;
            }}
            QTreeWidget::item {{ padding: 3px 4px; }}
            QTreeWidget::item:selected {{ background: rgba(0,240,255,0.12); border-left: 2px solid {C.CYAN}; }}
            QHeaderView::section {{
                background: {C.PANEL3}; color: {C.CYAN}; border: none;
                font-weight: bold; font-size: 8pt; padding: 5px 6px;
                border-bottom: 1px solid {C.CYAN};
            }}
            QScrollBar:vertical {{ background: {C.PANEL}; width: 6px; border: none; }}
            QScrollBar::handle:vertical {{ background: {C.BORDER}; border-radius: 3px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        layout.addWidget(self._proc_table, 1)

        return page

    # ════════════════════════════════════════════════
    #  PAGE: SECURITY
    # ════════════════════════════════════════════════
    def _build_security_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)

        t = QLabel(T("sec_title"))
        t.setFont(QFont("Consolas", 16, QFont.Bold))
        t.setStyleSheet(f"color: {C.ORANGE};")
        layout.addWidget(t)

        desc = QLabel(T("sec_desc"))
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {C.DIM};")
        layout.addWidget(desc)
        layout.addSpacing(8)

        # Status badge
        self._sec_status = QLabel(T("sec_safe"))
        self._sec_status.setFont(QFont("Consolas", 12, QFont.Bold))
        self._sec_status.setStyleSheet(f"color: {C.GREEN}; background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 8px; padding: 12px;")
        layout.addWidget(self._sec_status)
        layout.addSpacing(8)

        scan_btn = QPushButton(T("sec_scan"))
        scan_btn.setFont(QFont("Consolas", 11, QFont.Bold))
        scan_btn.setCursor(Qt.PointingHandCursor)
        scan_btn.setFixedHeight(44)
        scan_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.ORANGE}; color: {C.BG}; border: none; border-radius: 10px; padding: 12px; }}
            QPushButton:hover {{ background: {C.YELLOW}; }}
        """)
        scan_btn.clicked.connect(self._scan_security)
        layout.addWidget(scan_btn)
        layout.addSpacing(8)

        # Startup apps section
        st_label = QLabel(T("sec_startup"))
        st_label.setFont(QFont("Consolas", 10, QFont.Bold))
        st_label.setStyleSheet(f"color: {C.ORANGE};")
        layout.addWidget(st_label)

        self._sec_tree = QTreeWidget()
        self._sec_tree.setHeaderLabels([T("mon_name"), T("sec_location"), T("sec_status")])
        self._sec_tree.setColumnWidth(0, 300)
        self._sec_tree.setColumnWidth(1, 500)
        self._sec_tree.setColumnWidth(2, 100)
        self._sec_tree.setRootIsDecorated(False)
        self._sec_tree.setAlternatingRowColors(True)
        self._sec_tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {C.PANEL}; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 8px;
                font-family: 'Consolas'; font-size: 9pt;
                alternate-background-color: {C.PANEL2}; outline: none;
            }}
            QTreeWidget::item {{ padding: 4px; }}
            QTreeWidget::item:selected {{ background: rgba(255,180,60,0.12); }}
            QHeaderView::section {{
                background: {C.PANEL3}; color: {C.ORANGE}; border: none;
                font-weight: bold; font-size: 8pt; padding: 5px 6px;
                border-bottom: 1px solid {C.ORANGE};
            }}
            QScrollBar:vertical {{ background: {C.PANEL}; width: 6px; border: none; }}
            QScrollBar::handle:vertical {{ background: {C.BORDER}; border-radius: 3px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        layout.addWidget(self._sec_tree, 1)

        return page

    # ════════════════════════════════════════════════
    #  PAGE: DRIVERS
    # ════════════════════════════════════════════════
    def _build_drivers_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)

        t = QLabel(T("drv_title"))
        t.setFont(QFont("Consolas", 16, QFont.Bold))
        t.setStyleSheet(f"color: {C.CYAN_D};")
        layout.addWidget(t)

        desc = QLabel(T("drv_desc"))
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {C.DIM};")
        layout.addWidget(desc)
        layout.addSpacing(8)

        scan_btn = QPushButton(T("drv_scan"))
        scan_btn.setFont(QFont("Consolas", 11, QFont.Bold))
        scan_btn.setCursor(Qt.PointingHandCursor)
        scan_btn.setFixedHeight(44)
        scan_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.CYAN_D}; color: {C.BG}; border: none; border-radius: 10px; padding: 12px; }}
            QPushButton:hover {{ background: {C.CYAN}; }}
        """)
        scan_btn.clicked.connect(self._scan_drivers)
        layout.addWidget(scan_btn)
        layout.addSpacing(8)

        self._drv_tree = QTreeWidget()
        self._drv_tree.setHeaderLabels([T("drv_device"), T("drv_version"), T("drv_date"), T("drv_status_col")])
        self._drv_tree.setColumnWidth(0, 400)
        self._drv_tree.setColumnWidth(1, 200)
        self._drv_tree.setColumnWidth(2, 150)
        self._drv_tree.setColumnWidth(3, 100)
        self._drv_tree.setRootIsDecorated(False)
        self._drv_tree.setAlternatingRowColors(True)
        self._drv_tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {C.PANEL}; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 8px;
                font-family: 'Consolas'; font-size: 9pt;
                alternate-background-color: {C.PANEL2}; outline: none;
            }}
            QTreeWidget::item {{ padding: 4px; }}
            QTreeWidget::item:selected {{ background: rgba(0,184,196,0.12); }}
            QHeaderView::section {{
                background: {C.PANEL3}; color: {C.CYAN_D}; border: none;
                font-weight: bold; font-size: 8pt; padding: 5px 6px;
                border-bottom: 1px solid {C.CYAN_D};
            }}
            QScrollBar:vertical {{ background: {C.PANEL}; width: 6px; border: none; }}
            QScrollBar::handle:vertical {{ background: {C.BORDER}; border-radius: 3px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        layout.addWidget(self._drv_tree, 1)
        return page

    # ════════════════════════════════════════════════
    #  PAGE: TWEAKS
    # ════════════════════════════════════════════════
    def _build_tweaks_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)

        t = QLabel(T("twk_title"))
        t.setFont(QFont("Consolas", 16, QFont.Bold))
        t.setStyleSheet(f"color: {C.YELLOW};")
        layout.addWidget(t)

        desc = QLabel(T("twk_desc"))
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {C.DIM};")
        layout.addWidget(desc)
        layout.addSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll_w = QWidget()
        scroll_l = QVBoxLayout(scroll_w)
        scroll_l.setSpacing(6)

        tweaks = [
            ("twk_telemetry", "twk_telemetry_d",
             'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && sc stop DiagTrack >nul 2>&1 && sc config DiagTrack start=disabled >nul 2>&1'),
            ("twk_cortana", "twk_cortana_d",
             'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f'),
            ("twk_ads", "twk_ads_d",
             'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f'),
            ("twk_tips", "twk_tips_d",
             'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v SubscribedContent-338388Enabled /t REG_DWORD /d 0 /f'),
            ("twk_fastboot", "twk_fastboot_d",
             'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v HiberbootEnabled /t REG_DWORD /d 1 /f'),
            ("twk_visual", "twk_visual_d",
             'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f'),
            ("twk_sysmain", "twk_sysmain_d",
             "sc stop SysMain >nul 2>&1 && sc config SysMain start=disabled >nul 2>&1"),
            ("twk_wsearch", "twk_wsearch_d",
             "sc stop WSearch >nul 2>&1 && sc config WSearch start=disabled >nul 2>&1"),
            ("twk_hibernate", "twk_hibernate_d",
             "powercfg /h off"),
            ("twk_network", "twk_network_d",
             'reg add "HKLM\\SOFTWARE\\Microsoft\\MSMQ\\Parameters" /v TCPNoDelay /t REG_DWORD /d 1 /f'),
            ("twk_fastshut", "twk_fastshut_d",
             'reg add "HKCU\\Control Panel\\Desktop" /v WaitToKillAppTimeout /t REG_SZ /d "2000" /f'),
            ("twk_gamemode", "twk_gamemode_d",
             'reg add "HKCU\\Software\\Microsoft\\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f'),
        ]

        for name_key, desc_key, cmd in tweaks:
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: {C.PANEL}; border: 1px solid {C.BORDER};
                    border-radius: 8px;
                }}
                QFrame:hover {{ border-color: {C.YELLOW}; }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 10, 14, 10)
            info = QVBoxLayout()
            name_lbl = QLabel(T(name_key))
            name_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            name_lbl.setStyleSheet(f"color: {C.TEXT}; border: none;")
            desc_lbl = QLabel(T(desc_key))
            desc_lbl.setFont(QFont("Segoe UI", 8))
            desc_lbl.setStyleSheet(f"color: {C.MUTED}; border: none;")
            info.addWidget(name_lbl)
            info.addWidget(desc_lbl)
            rl.addLayout(info, 1)

            toggle = ToggleSwitch(False)
            toggle.toggled.connect(lambda checked, c=cmd, n=name_key: self._apply_tweak(c, n, checked))
            rl.addWidget(toggle)
            scroll_l.addWidget(row)

        # Quick actions
        qa_label = QLabel(T("twk_quick"))
        qa_label.setFont(QFont("Consolas", 10, QFont.Bold))
        qa_label.setStyleSheet(f"color: {C.YELLOW};")
        scroll_l.addWidget(qa_label)

        quick_actions = [
            ("chkdsk C: /scan", "chkdsk C:"),
            ("Disk Cleanup (cleanmgr)", "cleanmgr /lowdisk"),
            ("Defragment (dfrgui)", "dfrgui"),
            ("Task Manager → Startup", "taskmgr /0 /startup"),
            ("Services (services.msc)", "services.msc"),
            ("Flush DNS", "ipconfig /flushdns"),
        ]
        for label, cmd in quick_actions:
            btn = QPushButton(f"  ▶ {label}")
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
            scroll_l.addWidget(btn)

        scroll_l.addStretch()
        scroll.setWidget(scroll_w)
        layout.addWidget(scroll, 1)
        return page

    # ════════════════════════════════════════════════
    #  PAGE: PLUGINS
    # ════════════════════════════════════════════════
    def _build_plugins_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)

        t = QLabel(T("plg_title"))
        t.setFont(QFont("Consolas", 16, QFont.Bold))
        t.setStyleSheet(f"color: {C.PINK};")
        layout.addWidget(t)

        desc = QLabel(T("plg_desc"))
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {C.DIM};")
        layout.addWidget(desc)
        layout.addSpacing(8)

        # Template buttons
        tmpl_row = QHBoxLayout()
        tmpl_label = QLabel(T("plg_templates") + ":")
        tmpl_label.setFont(QFont("Consolas", 8, QFont.Bold))
        tmpl_label.setStyleSheet(f"color: {C.MUTED};")
        tmpl_row.addWidget(tmpl_label)

        templates = {
            T("plg_sysinfo"): "import platform, os\nprint(f'OS: {platform.system()} {platform.release()}')\nprint(f'Machine: {platform.machine()}')\nprint(f'Processor: {platform.processor()}')\nprint(f'User: {os.getlogin()}')\n",
            T("plg_proclist"): "import subprocess\nresult = subprocess.run(['tasklist', '/FO', 'TABLE'], capture_output=True, text=True)\nprint(result.stdout[:2000])\n",
            T("plg_diskinfo"): "import shutil, string\nfor letter in 'CDEFGH':\n    drive = f'{letter}:'\n    try:\n        t, u, f = shutil.disk_usage(drive + '\\\\\\\\')\n        print(f'{drive} Total={t//1024**3}GB Used={u//1024**3}GB Free={f//1024**3}GB')\n    except: pass\n",
            T("plg_netinfo"): "try:\n    import psutil\n    net = psutil.net_io_counters()\n    print(f'Sent: {net.bytes_sent//1024**2} MB')\n    print(f'Recv: {net.bytes_recv//1024**2} MB')\nexcept: print('psutil not available')\n",
        }
        for name, code in templates.items():
            btn = QPushButton(name)
            btn.setFont(QFont("Consolas", 8))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ background: {C.PANEL2}; color: {C.PINK}; border: 1px solid {C.BORDER}; border-radius: 6px; padding: 4px 10px; }}
                QPushButton:hover {{ background: {C.PINK}; color: white; }}
            """)
            btn.clicked.connect(lambda checked=False, c=code: self._plg_editor.setPlainText(c))
            tmpl_row.addWidget(btn)
        tmpl_row.addStretch()
        layout.addLayout(tmpl_row)
        layout.addSpacing(4)

        # Editor
        el = QLabel(T("plg_editor"))
        el.setFont(QFont("Consolas", 8, QFont.Bold))
        el.setStyleSheet(f"color: {C.PINK};")
        layout.addWidget(el)

        self._plg_editor = QPlainTextEdit()
        self._plg_editor.setFont(QFont("Consolas", 10))
        self._plg_editor.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {C.PANEL}; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 8px;
                padding: 8px;
            }}
        """)
        self._plg_editor.setPlainText("# Write your Python script here\nprint('Hello from s0meClean!')\n")
        layout.addWidget(self._plg_editor, 2)

        # Buttons
        btn_row = QHBoxLayout()
        run_btn = QPushButton(T("plg_run"))
        run_btn.setFont(QFont("Consolas", 11, QFont.Bold))
        run_btn.setCursor(Qt.PointingHandCursor)
        run_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.GREEN}, stop:1 {C.CYAN});
                color: {C.BG}; border: none; border-radius: 8px; padding: 10px 30px;
            }}
            QPushButton:hover {{ background: {C.GREEN}; }}
        """)
        run_btn.clicked.connect(self._run_plugin)
        btn_row.addWidget(run_btn)

        clear_btn = QPushButton(T("plg_clear"))
        clear_btn.setFont(QFont("Consolas", 9, QFont.Bold))
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.PANEL2}; color: {C.MUTED}; border: 1px solid {C.BORDER}; border-radius: 8px; padding: 10px 20px; }}
            QPushButton:hover {{ color: {C.RED}; border-color: {C.RED}; }}
        """)
        clear_btn.clicked.connect(lambda: self._plg_output.clear())
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Output
        ol = QLabel(T("plg_output"))
        ol.setFont(QFont("Consolas", 8, QFont.Bold))
        ol.setStyleSheet(f"color: {C.GREEN};")
        layout.addWidget(ol)

        self._plg_output = QPlainTextEdit()
        self._plg_output.setFont(QFont("Consolas", 9))
        self._plg_output.setReadOnly(True)
        self._plg_output.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {C.BG2}; color: {C.GREEN};
                border: 1px solid {C.BORDER}; border-radius: 8px;
                padding: 8px;
            }}
        """)
        layout.addWidget(self._plg_output, 1)
        return page

    # ════════════════════════════════════════════════
    #  PAGE: SETTINGS
    # ════════════════════════════════════════════════
    def _build_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)

        t = QLabel(T("settings_title"))
        t.setFont(QFont("Consolas", 16, QFont.Bold))
        t.setStyleSheet(f"color: {C.CYAN};")
        layout.addWidget(t)
        layout.addSpacing(12)

        # Language card
        lang_card = QFrame()
        lang_card.setStyleSheet(f"""
            QFrame {{ background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 12px; border-left: 4px solid {C.PURPLE}; }}
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
            QComboBox {{ background: {C.PANEL2}; color: {C.CYAN}; border: 1px solid {C.BORDER}; border-radius: 6px; padding: 6px 12px; min-width: 160px; }}
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
        layout.addSpacing(8)

        # About card
        about = QFrame()
        about.setStyleSheet(f"""
            QFrame {{ background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 12px; border-left: 4px solid {C.GREEN}; }}
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
        layout.addSpacing(8)

        # Key activation
        key_card = QFrame()
        key_card.setStyleSheet(f"""
            QFrame {{ background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 12px; border-left: 4px solid {C.CYAN}; }}
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
            QLineEdit {{ background: {C.PANEL2}; color: {C.TEXT}; border: 1px solid {C.BORDER}; border-radius: 6px; padding: 8px; letter-spacing: 2px; }}
        """)
        key_row.addWidget(self._key_input, 1)
        activate_btn = QPushButton(T("activate"))
        activate_btn.setFont(QFont("Consolas", 10, QFont.Bold))
        activate_btn.setCursor(Qt.PointingHandCursor)
        activate_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.CYAN}; color: {C.BG}; border: none; border-radius: 6px; padding: 8px 20px; }}
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

        self._load_key()
        layout.addStretch()
        return page

    # ── STATUS BAR ──
    def _build_statusbar(self, parent_layout):
        sb = QFrame()
        sb.setFixedHeight(32)
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
        st.setFont(QFont("Consolas", 7, QFont.Bold))
        st.setStyleSheet(f"color: {C.PINK};")
        sbl.addWidget(st)
        self._status_label = QLabel(T("ready"))
        self._status_label.setFont(QFont("Consolas", 9))
        self._status_label.setStyleSheet(f"color: {C.CYAN};")
        sbl.addWidget(self._status_label)
        sbl.addStretch()

        # Mini CPU/RAM in status bar
        self._sb_cpu = QLabel("CPU: —")
        self._sb_cpu.setFont(QFont("Consolas", 8))
        self._sb_cpu.setStyleSheet(f"color: {C.DIM};")
        self._sb_ram = QLabel("RAM: —")
        self._sb_ram.setFont(QFont("Consolas", 8))
        self._sb_ram.setStyleSheet(f"color: {C.DIM};")
        sbl.addWidget(self._sb_cpu)
        sbl.addSpacing(10)
        sbl.addWidget(self._sb_ram)

        parent_layout.addWidget(sb)

    # ═══════════════════════════════════════════════════
    #  ACTIONS
    # ═══════════════════════════════════════════════════
    def _switch_tab(self, key):
        pages = {"clean": 0, "boost": 1, "monitor": 2, "security": 3,
                 "drivers": 4, "tweaks": 5, "plugins": 6, "settings": 7}
        self._stack.setCurrentIndex(pages.get(key, 0))
        for k, btn in self._sidebar_btns.items():
            btn.set_active(k == key)
        self._rebuild_actions(key)

        # Load processes when switching to monitor
        if key == "monitor" and HAS_PSUTIL:
            self._refresh_processes()

    def _rebuild_actions(self, tab):
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
                (T("browser_cache"), C.PURPLE, False, lambda: self._start_scan("browser")),
            ]
        elif tab == "clean_custom":
            actions = [
                (T("scan_go"), C.PINK, True, lambda: self._start_scan("custom", self._custom_path_val if hasattr(self, '_custom_path_val') else "")),
            ]
        else:
            actions = []

        for text, color, bold, callback in actions:
            btn = QPushButton(text)
            btn.setFont(QFont("Consolas", 8, QFont.Bold if bold else QFont.Normal))
            btn.setCursor(Qt.PointingHandCursor)
            if bold:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 {color}, stop:1 rgba(0,0,0,0.1));
                        color: {C.BG}; border: none; border-radius: 8px; padding: 8px; text-align: left;
                    }}
                    QPushButton:hover {{ background: {color}; }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {C.PANEL2}; color: {color};
                        border: 1px solid rgba(42,54,96,0.5);
                        border-radius: 8px; padding: 6px 8px; text-align: left;
                    }}
                    QPushButton:hover {{
                        background: {color}; color: {C.BG}; border-color: {color};
                    }}
                """)
            btn.clicked.connect(callback)
            self._action_container.addWidget(btn)

    # ── SCAN MANAGEMENT ──
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
        self._switch_tab("clean")

    def _on_progress(self, pct, status):
        self._progress.setValue(pct)
        self._status_label.setText(status)

    def _on_item_found(self, item: ScanItem):
        self._scan_items.append(item)
        idx = len(self._scan_items)
        tw = QTreeWidgetItem([str(idx), format_size(item.size), item.path, item.details])
        tw.setData(1, Qt.UserRole, item.size)
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
        r = QMessageBox.question(self, T("confirm_del_t"), T("confirm_del_m", n=n),
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
                    parts = item.extra.split("\\")
                    if "WOW6432Node" in item.extra:
                        hkey = winreg.HKEY_LOCAL_MACHINE
                    elif "HKCU" in item.extra or "HKEY_CURRENT_USER" in item.extra:
                        hkey = winreg.HKEY_CURRENT_USER
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
                    subprocess.run(["powershell", "-NoProfile", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                                   capture_output=True, timeout=30)
                    ok += 1
                    freed += item.size
                elif item.item_type == "hibernation":
                    subprocess.run(["powercfg", "/h", "off"], capture_output=True, timeout=15)
                    ok += 1
                    freed += item.size
                elif item.item_type == "installed" and item.extra:
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

        QMessageBox.information(self, T("result_title"), T("result_msg", ok=ok, fail=fail, freed=format_size(freed)))
        self._update_disk_info()

    # ── GAME BOOST ──
    def _toggle_boost(self):
        if self._game_mode_active:
            self._disable_boost()
        else:
            self._enable_boost()

    def _enable_boost(self):
        applied = 0
        checks = self._boost_checks

        if checks["power"].isChecked():
            try:
                subprocess.run("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", shell=True, capture_output=True, timeout=10)
                applied += 1
            except Exception:
                pass

        if checks["services"].isChecked():
            services = ["SysMain", "DiagTrack", "WSearch"]
            for svc in services:
                try:
                    subprocess.run(f"sc stop {svc}", shell=True, capture_output=True, timeout=10)
                    applied += 1
                except Exception:
                    pass

        if checks["ram"].isChecked():
            try:
                subprocess.run("powershell -NoProfile -Command \"[System.GC]::Collect()\"", shell=True, capture_output=True, timeout=10)
                applied += 1
            except Exception:
                pass

        if checks["anim"].isChecked():
            try:
                subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f',
                             shell=True, capture_output=True, timeout=10)
                applied += 1
            except Exception:
                pass

        if checks["nagle"].isChecked():
            try:
                subprocess.run('reg add "HKLM\\SOFTWARE\\Microsoft\\MSMQ\\Parameters" /v TCPNoDelay /t REG_DWORD /d 1 /f',
                             shell=True, capture_output=True, timeout=10)
                applied += 1
            except Exception:
                pass

        if checks["overlay"].isChecked():
            if not self._overlay:
                self._overlay = OverlayWindow()
            self._overlay.show()

        self._game_mode_active = True
        self._boost_status.setText(T("boost_active"))
        self._boost_status.setStyleSheet(f"color: {C.GREEN}; border: none;")
        self._boost_btn.setText(T("boost_disable"))
        self._boost_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.RED}, stop:1 {C.PINK});
                color: white; border: none; border-radius: 10px; padding: 10px 30px;
            }}
            QPushButton:hover {{ background: {C.RED}; }}
        """)
        self._status_label.setText(T("boost_applied", n=applied))
        self._status_label.setStyleSheet(f"color: {C.GREEN};")

    def _disable_boost(self):
        # Restore services
        services = ["SysMain", "WSearch"]
        for svc in services:
            try:
                subprocess.run(f"sc start {svc}", shell=True, capture_output=True, timeout=10)
            except Exception:
                pass

        if self._overlay:
            self._overlay.hide()

        self._game_mode_active = False
        self._boost_status.setText(T("boost_inactive"))
        self._boost_status.setStyleSheet(f"color: {C.MUTED}; border: none;")
        self._boost_btn.setText(T("boost_enable"))
        self._boost_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.GREEN}, stop:1 {C.CYAN});
                color: {C.BG}; border: none; border-radius: 10px; padding: 10px 30px;
            }}
            QPushButton:hover {{ background: {C.GREEN}; }}
        """)
        self._status_label.setText(T("boost_restored"))
        self._status_label.setStyleSheet(f"color: {C.CYAN};")

    # ── MONITOR ──
    def _start_monitor(self):
        self._monitor_worker = MonitorWorker()
        self._monitor_worker.stats_update.connect(self._on_monitor_update)
        self._monitor_worker.start()

    def _on_monitor_update(self, stats):
        cpu = stats.get("cpu", 0)
        ram_pct = stats.get("ram_percent", 0)
        ram_used = stats.get("ram_used", 0)
        ram_total = stats.get("ram_total", 1)

        # Status bar
        self._sb_cpu.setText(f"CPU: {cpu:.0f}%")
        self._sb_cpu.setStyleSheet(f"color: {C.RED if cpu > 80 else C.CYAN};")
        self._sb_ram.setText(f"RAM: {ram_pct:.0f}%")
        self._sb_ram.setStyleSheet(f"color: {C.RED if ram_pct > 85 else C.PURPLE};")

        # Graphs
        if hasattr(self, '_graph_cpu'):
            self._graph_cpu.add_value(cpu)
            self._graph_cpu.set_text(f"{cpu:.0f}%")
            self._graph_ram.add_value(ram_pct)
            self._graph_ram.set_text(f"{format_size(ram_used)}/{format_size(ram_total)}")

            # Disk I/O rate
            disk_read = stats.get("disk_read", 0)
            disk_write = stats.get("disk_write", 0)
            if self._prev_disk_io is not None:
                dr = (disk_read - self._prev_disk_io[0]) / 1024 / 1024  # MB/s
                dw = (disk_write - self._prev_disk_io[1]) / 1024 / 1024
                disk_rate = dr + dw
                self._graph_disk.add_value(min(disk_rate * 10, 100))
                self._graph_disk.set_text(f"R:{dr:.1f} W:{dw:.1f} MB/s")
            self._prev_disk_io = (disk_read, disk_write)

            # Network rate
            net_sent = stats.get("net_sent", 0)
            net_recv = stats.get("net_recv", 0)
            if self._prev_net_io is not None:
                ns = (net_sent - self._prev_net_io[0]) / 1024  # KB/s
                nr = (net_recv - self._prev_net_io[1]) / 1024
                net_rate = ns + nr
                self._graph_net.add_value(min(net_rate / 10, 100))
                self._graph_net.set_text(f"↑{ns:.0f} ↓{nr:.0f} KB/s")
            self._prev_net_io = (net_sent, net_recv)

        # Boost page stats
        if hasattr(self, '_boost_cpu_label'):
            self._boost_cpu_label.setText(f"CPU: {cpu:.0f}%")
            self._boost_ram_label.setText(f"RAM: {ram_pct:.0f}%")

        # Overlay
        if self._overlay and self._overlay.isVisible():
            self._overlay.set_stats({
                "cpu": cpu,
                "ram": ram_pct,
                "gpu": "N/A",
                "net": f"{self._graph_net._current_text}" if hasattr(self, '_graph_net') else "—",
            })

    def _refresh_processes(self):
        if not HAS_PSUTIL:
            return
        self._proc_table.clear()
        try:
            procs = []
            for proc in psutil.process_iter(['name', 'pid', 'cpu_percent', 'memory_info']):
                try:
                    info = proc.info
                    mem = info['memory_info'].rss if info['memory_info'] else 0
                    procs.append((info['name'] or "—", info['pid'], info.get('cpu_percent', 0) or 0, mem))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            procs.sort(key=lambda x: x[3], reverse=True)
            for name, pid, cpu_p, mem in procs[:150]:
                tw = QTreeWidgetItem([name, str(pid), f"{cpu_p:.1f}", format_size(mem)])
                tw.setData(2, Qt.UserRole, cpu_p)
                tw.setData(3, Qt.UserRole, mem)
                self._proc_table.addTopLevelItem(tw)
        except Exception:
            pass

    def _kill_process(self):
        if not HAS_PSUTIL:
            return
        sel = self._proc_table.selectedItems()
        if not sel:
            return
        pid = int(sel[0].text(1))
        name = sel[0].text(0)
        r = QMessageBox.question(self, T("confirm_title"), f"Kill process {name} (PID: {pid})?",
                                 QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes:
            try:
                proc = psutil.Process(pid)
                proc.kill()
                self._refresh_processes()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    # ── SECURITY ──
    def _scan_security(self):
        self._sec_tree.clear()
        warnings = 0

        # Check startup items
        startup_locations = [
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKCU\\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKLM\\Run"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce", "HKCU\\RunOnce"),
        ]
        for hkey, path, label in startup_locations:
            try:
                key = winreg.OpenKey(hkey, path)
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        tw = QTreeWidgetItem([name, f"{label}: {value}", "Active"])
                        tw.setForeground(0, QColor(C.TEXT))
                        tw.setForeground(1, QColor(C.DIM))
                        tw.setForeground(2, QColor(C.GREEN))
                        self._sec_tree.addTopLevelItem(tw)
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except OSError:
                pass

        # Check for suspicious processes
        if HAS_PSUTIL:
            suspicious_names = {"cryptominer", "miner", "xmrig", "coinhive", "nicehash"}
            for proc in psutil.process_iter(['name', 'pid', 'cpu_percent']):
                try:
                    pname = (proc.info['name'] or "").lower()
                    cpu_p = proc.info.get('cpu_percent', 0) or 0
                    if any(s in pname for s in suspicious_names) or cpu_p > 80:
                        tw = QTreeWidgetItem([proc.info['name'], f"PID: {proc.info['pid']}", "⚠ Suspicious"])
                        tw.setForeground(0, QColor(C.RED))
                        tw.setForeground(2, QColor(C.RED))
                        self._sec_tree.addTopLevelItem(tw)
                        warnings += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        if warnings > 0:
            self._sec_status.setText(T("sec_warning"))
            self._sec_status.setStyleSheet(f"color: {C.YELLOW}; background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 8px; padding: 12px;")
        else:
            self._sec_status.setText(T("sec_safe"))
            self._sec_status.setStyleSheet(f"color: {C.GREEN}; background: {C.PANEL}; border: 1px solid {C.BORDER}; border-radius: 8px; padding: 12px;")

    # ── DRIVERS ──
    def _scan_drivers(self):
        self._drv_tree.clear()
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-WmiObject Win32_PnPSignedDriver | Where-Object { $_.DeviceName -ne $null } | "
                 "Select-Object DeviceName, DriverVersion, DriverDate | ConvertTo-Csv -NoTypeInformation"],
                capture_output=True, text=True, timeout=30
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = line.strip('"').split('","')
                    if len(parts) >= 3:
                        name = parts[0].strip('"')
                        version = parts[1].strip('"') if len(parts) > 1 else "—"
                        date_raw = parts[2].strip('"') if len(parts) > 2 else "—"
                        # Parse date
                        date_str = date_raw[:8] if len(date_raw) >= 8 and date_raw[:4].isdigit() else date_raw
                        if len(date_str) == 8 and date_str.isdigit():
                            date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

                        tw = QTreeWidgetItem([name, version, date_str, T("drv_ok")])
                        tw.setForeground(3, QColor(C.GREEN))
                        self._drv_tree.addTopLevelItem(tw)
        except Exception as e:
            tw = QTreeWidgetItem([f"Error: {e}", "", "", ""])
            self._drv_tree.addTopLevelItem(tw)

    # ── TWEAKS ──
    def _apply_tweak(self, cmd, name_key, checked):
        if checked:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=15)
                self._status_label.setText(f"{T(name_key)}: {T('twk_applied')}")
                self._status_label.setStyleSheet(f"color: {C.GREEN};")
            except Exception:
                self._status_label.setText(f"{T(name_key)}: {T('twk_error')}")
                self._status_label.setStyleSheet(f"color: {C.RED};")

    # ── PLUGINS ──
    def _run_plugin(self):
        code = self._plg_editor.toPlainText()
        self._plg_output.appendPlainText(f">>> {T('plg_running')}")
        self._status_label.setText(T("plg_running"))

        def _exec():
            import io
            old_stdout = sys.stdout
            sys.stdout = mystdout = io.StringIO()
            try:
                exec(code, {"__builtins__": __builtins__})
                output = mystdout.getvalue()
            except Exception:
                output = traceback.format_exc()
            finally:
                sys.stdout = old_stdout
            return output

        def _thread():
            result = _exec()
            QTimer.singleShot(0, lambda: self._on_plugin_done(result))

        threading.Thread(target=_thread, daemon=True).start()

    def _on_plugin_done(self, result):
        self._plg_output.appendPlainText(result)
        self._plg_output.appendPlainText(f"--- {T('plg_done')} ---\n")
        self._status_label.setText(T("plg_done"))
        self._status_label.setStyleSheet(f"color: {C.GREEN};")

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
