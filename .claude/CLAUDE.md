# s0meClean? — Project Rules

## Version Sync Rule
When changing the app version (`VERSION` in `app/main.py`), ALWAYS update the version in ALL of these locations:
1. `app/main.py` — line `VERSION = "X.Y.Z"`
2. `index.html` — the version string in the footer/status line (search for `vX.Y.Z`)
3. `admin.html` — if version is mentioned anywhere
4. Git tag — create a matching `vX.Y.Z` tag

## Git Workflow
- Commit and push changes automatically without asking — permissions are pre-approved
- Use conventional commit style: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- Always include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>` trailer
- After pushing code changes, build the EXE if relevant and update the GitHub Release

## Project Structure
- `app/main.py` — Main PySide6 application (~2300 lines)
- `index.html` — Landing page (GitHub Pages)
- `admin.html` — Admin panel for key management
- `build.bat` — PyInstaller build script
- `app/bin/` — External tools (BleachBit portable)

## i18n
- All user-facing strings use `T("key")` function
- Languages: English (EN), Russian (RU)
- Language preference saved in `config.json`
- `STRINGS` dict in main.py holds all translations

## Tech Stack
- Python 3 + PySide6 (Qt)
- PyInstaller (--onedir)
- GitHub Pages for site
- GitHub Releases for distribution
