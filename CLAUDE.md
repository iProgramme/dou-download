# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Douyin (TikTok China) video batch downloader. Consists of two modes:

1. **CLI mode** (`download_user.py`) — original single-file script, unchanged
2. **Desktop GUI** (`app.py`) — cross-platform client using Flask + pywebview

Both wrap the [`f2`](https://github.com/Johnserf-Seed/f2) CLI tool for actual downloading.

## Running

**Desktop app:**
```bash
pip install -r requirements.txt
python3 app.py
```

**CLI mode:**
```bash
python3 download_user.py <douyin_user_url>
```

**Headless mode (no GUI):**
```bash
python3 app.py --no-gui
```

## Architecture

```
app.py              — Flask routes + pywebview launcher (entry point)
database.py         — SQLite layer (settings, tasks, history tables)
downloader.py       — Wraps f2 CLI, parses output, returns structured results
scheduler.py        — APScheduler recurring downloads, restores tasks from DB on startup
download_user.py    — Original CLI script (do not modify)
templates/index.html — Single-page frontend
static/css/style.css — Styling
static/js/app.js    — Frontend logic (navigation, API calls, real-time status)
```

**Data flow:** Frontend → Flask API → downloader.py → subprocess `f2 dy -M post` → downloads/

**Database:** `douyin_downloader.db` (SQLite) stores cookie, download path, scheduled tasks, and download history. Separate from `douyin_users.db` which is managed by f2.

## Dependencies

- Python 3.13+
- `f2` v0.0.1.7 (global pip install, not vendored)
- `flask`, `pywebview`, `apscheduler` (see requirements.txt)

## Packaging

Build scripts for standalone executables:
- Mac: `./build_mac.sh` → `dist/抖音视频下载器/`
- Windows: `build_windows.bat` → `dist\抖音视频下载器\`

Uses PyInstaller. Note: `--add-data` separator differs by platform (`:` on Mac, `;` on Windows).

## Key Details

- Cookie is stored in SQLite settings table, not in source code (GUI mode) or hardcoded (CLI mode)
- Download is single-threaded (one download at a time, controlled by a threading lock)
- APScheduler runs in background, restores tasks from DB on app restart
- Folder browse uses pywebview's native file dialog via JS API bridge
