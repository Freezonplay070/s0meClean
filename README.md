# s0meClean v2.0.0

> Premium System Optimization Suite — PyQt6, frameless, Mica-blur, neon cyberpunk theme.

## Features

- **Cleaner** — junk, temp, browser caches, phantom registry entries, orphan folders
- **Boost** — one-click Game Mode (kills background processes, frees RAM, swaps power plan, hot-swaps theme to aggressive orange/red)
- **Monitor** — live CPU / RAM / Disk stats
- **AI Terminal** — smart command parsing (e.g. `check dota folder` → finds Steam path, analyzes caches)
- **Drivers** — version check + bulk update
- **Live Updates** — auto-checks GitHub Releases, downloads in background with animated progress
- **UI** — frameless window, Windows 11 Mica backdrop, custom QSS theme with hot-swap, animated tab transitions, neon glow buttons

## Stack

- PyQt6 + qtawesome + PyQt6-Fluent-Widgets
- DWM API (ctypes) for Mica/Acrylic
- Custom QSS with token substitution (theme hot-swap)
- QThread-based GitHub Releases updater with cancellation

## Install

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py
```

## Build .exe

```bash
pip install pyinstaller
pyinstaller s0meClean.spec
# output: dist/s0meClean.exe
```

## Auto-release

Push a tag `v*` and GitHub Actions builds and publishes a Release with the .exe asset:

```bash
git tag v2.0.0
git push origin v2.0.0
```

## Project structure

```
s0meClean/
├── main.py                  # entry
├── app/
│   ├── main_window.py       # frameless host
│   ├── title_bar.py         # drag + win controls
│   ├── sidebar.py           # nav + gradient indicator
│   ├── widgets/             # PremiumGlowButton, AnimatedPage
│   ├── pages/               # cleaner / boost / monitor / settings
│   ├── core/                # github_updater, win_effects
│   └── styles/              # theme + qss
└── resources/
```

## License

MIT
