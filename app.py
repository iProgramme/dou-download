import os
import sys
import threading
import json
from flask import Flask, request, jsonify, render_template

import database
import downloader
import scheduler

app = Flask(__name__, static_folder="static", template_folder="templates")


# --- Web Routes ---

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    f2_err = check_f2()
    return jsonify({"f2_ok": f2_err is None, "f2_error": f2_err or ""})


# --- Settings API ---

@app.route("/api/settings", methods=["GET"])
def get_settings():
    return jsonify(database.get_all_settings())


@app.route("/api/settings", methods=["PUT"])
def update_settings():
    data = request.get_json()
    for key in ("cookie", "download_path"):
        if key in data:
            database.set_setting(key, data[key])
    return jsonify({"ok": True})


# --- Download API ---

@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.get_json()
    user_input = data.get("url", "").strip()
    if not user_input:
        return jsonify({"ok": False, "message": "请输入博主链接或用户 ID"}), 400

    cookie = database.get_setting("cookie")
    if not cookie:
        return jsonify({"ok": False, "message": "请先在设置页面配置 Cookie"}), 400

    def _run():
        downloader.run_download_with_history(user_input)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return jsonify({"ok": True, "message": "下载任务已启动"})


@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify(downloader.get_current_status())


# --- Tasks API ---

@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    return jsonify(database.get_all_tasks())


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    user_input = data.get("url", "").strip()
    interval = data.get("interval_hours", 6)
    if not user_input:
        return jsonify({"ok": False, "message": "请输入博主链接或用户 ID"}), 400
    try:
        interval = int(interval)
        if interval < 1:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"ok": False, "message": "间隔时间必须为正整数"}), 400

    url = downloader.normalize_url(user_input)
    task_id = scheduler.add_task(url, interval)
    return jsonify({"ok": True, "task_id": task_id})


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    if "enabled" in data:
        scheduler.toggle_task(task_id, bool(data["enabled"]))
    if "interval_hours" in data:
        try:
            interval = int(data["interval_hours"])
            if interval < 1:
                raise ValueError
            scheduler.update_task_interval(task_id, interval)
        except (ValueError, TypeError):
            return jsonify({"ok": False, "message": "间隔时间必须为正整数"}), 400
    return jsonify({"ok": True})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    scheduler.remove_task(task_id)
    return jsonify({"ok": True})


@app.route("/api/tasks/<int:task_id>/run", methods=["POST"])
def run_task(task_id):
    def _run():
        scheduler.run_task_now(task_id)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return jsonify({"ok": True, "message": "手动执行已启动"})


# --- History API ---

@app.route("/api/history", methods=["GET"])
def list_history():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    offset = (page - 1) * per_page
    items = database.get_history(limit=per_page, offset=offset)
    total = database.get_history_count()
    return jsonify({"items": items, "total": total, "page": page, "per_page": per_page})


@app.route("/api/history/<int:hist_id>", methods=["DELETE"])
def delete_history(hist_id):
    database.delete_history(hist_id)
    return jsonify({"ok": True})


# --- Folder Browse (handled via pywebview JS API, but also support POST fallback) ---

@app.route("/api/browse-folder", methods=["POST"])
def browse_folder_fallback():
    # This endpoint is a fallback; the real folder dialog is handled by pywebview's JS API
    return jsonify({"ok": False, "message": "请使用应用内的文件夹选择按钮"})


# --- pywebview JS API ---

class Api:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def browse_folder(self):
        import webview
        if self._window is None:
            return ""
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            return result[0]
        return ""


# --- Main ---

def check_f2():
    """Check if f2 CLI is available. Returns error message or None."""
    import shutil
    if shutil.which("f2"):
        return None
    # Also check common paths (same as downloader.get_f2_path)
    possible_paths = [
        os.path.expanduser("~/.local/bin/f2"),
        "/usr/local/bin/f2",
        os.path.join(sys.prefix, "bin", "f2"),
        "/Library/Frameworks/Python.framework/Versions/3.13/bin/f2",
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return None
    return "未找到 f2 下载引擎。请在终端运行: pip install f2"


def main():
    database.init_db()
    scheduler.init_scheduler()

    f2_err = check_f2()
    if f2_err:
        print(f"⚠️  {f2_err}")

    if "--no-gui" in sys.argv:
        port = int(os.environ.get("PORT", 5000))
        print(f"Starting server at http://localhost:{port}")
        app.run(host="127.0.0.1", port=port, debug=False)
    else:
        try:
            import webview

            api = Api()
            window = webview.create_window(
                "抖音视频下载器",
                app,
                js_api=api,
                width=1100,
                height=750,
                min_size=(900, 600),
                text_select=True,
            )
            api.set_window(window)

            def on_closed():
                scheduler.shutdown()

            window.events.closed += on_closed
            webview.start(debug=False)
        except ImportError:
            print("pywebview 未安装，将以命令行模式启动。安装: pip install pywebview")
            port = int(os.environ.get("PORT", 5000))
            print(f"Starting server at http://localhost:{port}")
            app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
