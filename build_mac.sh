#!/bin/bash
# Build Mac .app using PyInstaller
# Run: chmod +x build_mac.sh && ./build_mac.sh

set -e

echo "Installing dependencies..."
python3 -m pip install -r requirements.txt pyinstaller

echo "Building Mac app..."
python3 -m PyInstaller \
    --name "抖音视频下载器" \
    --onedir \
    --windowed \
    --add-data "static:static" \
    --add-data "templates:templates" \
    --add-data "download_user.py:." \
    --hidden-import "webview" \
    --hidden-import "webview.platforms.cocoa" \
    --hidden-import "apscheduler.schedulers.background" \
    --hidden-import "apscheduler.triggers.interval" \
    --noconfirm \
    app.py

echo "Build complete! App is in dist/抖音视频下载器/"
