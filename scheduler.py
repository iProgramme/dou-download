import threading
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import database
import downloader

_scheduler = None
_lock = threading.Lock()


def init_scheduler():
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = BackgroundScheduler()
    _scheduler.start()
    _restore_tasks()


def _restore_tasks():
    """Re-register all enabled tasks from the database on startup."""
    tasks = database.get_enabled_tasks()
    for task in tasks:
        _add_job(task["id"], task["user_url"], task["interval_hours"])


def _job_wrapper(task_id):
    """Execute a scheduled download and record history."""
    task = database.get_task(task_id)
    if not task or not task["enabled"]:
        return
    downloader.run_download_with_history(task["user_url"], task_id=task_id)


def _add_job(task_id, user_url, interval_hours):
    """Add a job to the scheduler."""
    job_id = f"task_{task_id}"
    # Remove existing job if any
    try:
        _scheduler.remove_job(job_id)
    except Exception:
        pass
    _scheduler.add_job(
        _job_wrapper,
        trigger=IntervalTrigger(hours=interval_hours),
        id=job_id,
        args=[task_id],
        next_run_time=datetime.now() + timedelta(hours=interval_hours),
        replace_existing=True,
    )


def add_task(user_url, interval_hours, nickname=""):
    """Create a new scheduled task and register it."""
    task_id = database.create_task(user_url, interval_hours, nickname)
    next_run = (datetime.now() + timedelta(hours=interval_hours)).isoformat(timespec="seconds")
    database.update_task(task_id, next_run=next_run)
    _add_job(task_id, user_url, interval_hours)
    return task_id


def remove_task(task_id):
    """Remove a scheduled task."""
    job_id = f"task_{task_id}"
    try:
        _scheduler.remove_job(job_id)
    except Exception:
        pass
    database.delete_task(task_id)


def toggle_task(task_id, enabled):
    """Enable or disable a task."""
    database.update_task(task_id, enabled=int(enabled))
    job_id = f"task_{task_id}"
    if enabled:
        task = database.get_task(task_id)
        if task:
            _add_job(task_id, task["user_url"], task["interval_hours"])
    else:
        try:
            _scheduler.remove_job(job_id)
        except Exception:
            pass
        database.update_task(task_id, next_run=None)


def update_task_interval(task_id, interval_hours):
    """Update the interval for an existing task."""
    database.update_task(task_id, interval_hours=interval_hours)
    task = database.get_task(task_id)
    if task and task["enabled"]:
        _add_job(task_id, task["user_url"], interval_hours)
        next_run = (datetime.now() + timedelta(hours=interval_hours)).isoformat(timespec="seconds")
        database.update_task(task_id, next_run=next_run)


def run_task_now(task_id):
    """Manually trigger a task immediately."""
    task = database.get_task(task_id)
    if not task:
        return None
    return downloader.run_download_with_history(task["user_url"], task_id=task_id)


def shutdown():
    if _scheduler:
        _scheduler.shutdown(wait=False)
