import os
import sys
import re
import subprocess
import shutil
import threading
from datetime import datetime

import database

_download_lock = threading.Lock()
_current_status = {"running": False, "user_url": "", "log": [], "progress": ""}


def get_f2_path():
    f2_bin = shutil.which("f2")
    if f2_bin:
        return f2_bin
    possible_paths = [
        os.path.expanduser("~/.local/bin/f2"),
        "/usr/local/bin/f2",
        os.path.join(sys.prefix, "bin", "f2"),
        "/Library/Frameworks/Python.framework/Versions/3.13/bin/f2",
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return "f2"


def normalize_url(user_input):
    """Accept a Douyin user URL or a bare user ID and return a full URL."""
    user_input = user_input.strip()
    if not user_input:
        return None
    if user_input.startswith("http"):
        return user_input
    # Treat as user ID — build the canonical profile URL
    return f"https://www.douyin.com/user/{user_input}"


def get_current_status():
    return dict(_current_status)


def _parse_video_count(output_lines):
    """Try to extract video download count from f2 stdout."""
    count = 0
    for line in output_lines:
        # f2 output patterns: look for download completion indicators
        if "下载完成" in line or "download" in line.lower():
            count += 1
        # Also match patterns like "共 X 个" or "Total: X"
        m = re.search(r"共\s*(\d+)\s*个", line)
        if m:
            count = max(count, int(m.group(1)))
    return count


def run_download(user_input):
    """Run a one-time download. Returns (success, video_count, message)."""
    url = normalize_url(user_input)
    if not url:
        return False, 0, "请输入有效的博主链接或用户 ID"

    cookie = database.get_setting("cookie")
    if not cookie:
        return False, 0, "请先在设置页面配置 Cookie"

    download_path = database.get_setting("download_path") or os.path.expanduser(
        "~/Desktop/DouyinDownloader/downloads"
    )
    os.makedirs(download_path, exist_ok=True)

    if not _download_lock.acquire(blocking=False):
        return False, 0, "已有下载任务正在执行，请等待完成后再试"

    try:
        _current_status["running"] = True
        _current_status["user_url"] = url
        _current_status["log"] = []
        _current_status["progress"] = "正在启动下载引擎..."

        f2_path = get_f2_path()
        cmd = [f2_path, "dy", "-u", url, "-p", download_path, "-k", cookie, "-M", "post"]

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        output_lines = []
        for line in process.stdout:
            line = line.rstrip("\n")
            output_lines.append(line)
            _current_status["log"].append(line)
            _current_status["progress"] = line[:120]

        process.wait()
        video_count = _parse_video_count(output_lines)

        if process.returncode == 0:
            _current_status["progress"] = f"完成！下载 {video_count} 个视频"
            return True, video_count, f"下载完成，共 {video_count} 个视频"
        else:
            msg = f"f2 退出码 {process.returncode}"
            _current_status["progress"] = msg
            return False, 0, msg

    except FileNotFoundError:
        return False, 0, "未找到 f2 命令，请先安装: pip install f2"
    except Exception as e:
        return False, 0, str(e)
    finally:
        _download_lock.release()
        _current_status["running"] = False


def run_download_with_history(user_input, task_id=None):
    """Run download and record to history. Returns result dict."""
    url = normalize_url(user_input)
    if not url:
        return {"success": False, "video_count": 0, "message": "无效的链接"}

    hist_id = database.create_history(url, task_id=task_id)
    success, video_count, message = run_download(user_input)
    status = "success" if success else "failed"
    database.finish_history(hist_id, status, video_count, message)

    # Update task last_run and nickname if applicable
    if task_id:
        database.update_task(task_id, last_run=datetime.now().isoformat(timespec="seconds"))

    return {"success": success, "video_count": video_count, "message": message, "history_id": hist_id}
