@echo off
title s0meClean? Build
cd /d "%~dp0"

echo [BUILD] s0meClean? — Cyberpunk Disk Cleaner
echo.

if not exist venv (
    echo [1/4] Creating virtual environment...
    python -m venv venv
)

echo [2/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install PySide6 psutil pyinstaller -q

echo [3/4] Building EXE...
pyinstaller --noconfirm --onedir --windowed ^
    --name "s0meClean" ^
    --version-file "app\version_info.py" ^
    --add-data "app\bin;bin" ^
    "app\main.py"

echo [4/4] Creating ZIP...
cd dist
if exist s0meClean.zip del s0meClean.zip
powershell -NoProfile -Command "Compress-Archive -Path 's0meClean' -DestinationPath 's0meClean.zip' -Force"
cd ..

echo.
echo [DONE] Build complete: dist\s0meClean.zip
pause
