@echo off
REM Build Windows .exe using PyInstaller
REM Run: build_windows.bat

echo Installing dependencies...
python -m pip install -r requirements.txt pyinstaller

echo Building Windows exe...
python -m PyInstaller ^
    --name "抖音视频下载器" ^
    --onedir ^
    --windowed ^
    --add-data "static;static" ^
    --add-data "templates;templates" ^
    --add-data "download_user.py;." ^
    --hidden-import "webview" ^
    --hidden-import "webview.platforms.edgechromium" ^
    --hidden-import "apscheduler.schedulers.background" ^
    --hidden-import "apscheduler.triggers.interval" ^
    --noconfirm ^
    app.py

echo Build complete! Exe is in dist\抖音视频下载器\
pause
