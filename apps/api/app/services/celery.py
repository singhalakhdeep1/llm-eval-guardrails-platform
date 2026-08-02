# Celery integration for llm-eval-guardrails-platform

from celery import Celery
from celery.schedules import crontab
import os

class CeleryService:
    def __init__(self):
        self.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        self.result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
        self.app = Celery(
            "llm_eval_tasks",
            broker=self.broker_url,
            backend=self.result_backend
        )
        self._configure()

    def _configure(self):
        """Configure Celery"""
        self.app.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="UTC",
            enable_utc=True,
            task_track_started=True,
            task_time_limit=30 * 60,  # 30 minutes
            task_soft_time_limit=25 * 60,  # 25 minutes
            worker_prefetch_multiplier=4,
            worker_max_tasks_per_child=1000,
        )

        self.app.conf.beat_schedule = {
            "cleanup-old-runs": {
                "task": "tasks.cleanup_old_runs",
                "schedule": crontab(hour=0, minute=0),
            },
            "sync-metrics": {
                "task": "tasks.sync_metrics",
                "schedule": crontab(minute="*/5"),
            },
        }

    def task(self, name: str = None):
        """Decorator for creating tasks"""
        def decorator(func):
            return self.app.task(name=name)(func)
        return decorator

    def send_task(self, task_name: str, args: list = None, kwargs: dict = None):
        """Send a task"""
        return self.app.send_task(task_name, args=args, kwargs=kwargs)

    def delay(self, task_name: str, *args, **kwargs):
        """Delay a task"""
        return self.app.send_task(task_name, args=args, kwargs=kwargs)

    def apply_async(self, task_name: str, args=None, kwargs=None, countdown=None, eta=None):
        """Apply a task with options"""
        return self.app.send_task(
            task_name,
            args=args,
            kwargs=kwargs,
            countdown=countdown,
            eta=eta
        )

    def get_result(self, task_id: str):
        """Get task result"""
        return self.app.AsyncResult(task_id)

    def revoke(self, task_id: str, terminate: bool = False):
        """Revoke a task"""
        return self.app.control.revoke(task_id, terminate=terminate)

    def inspect(self):
        """Get Celery inspect instance"""
        return self.app.control.inspect()

    def active_tasks(self):
        """Get active tasks"""
        return self.inspect().active()

    def scheduled_tasks(self):
        """Get scheduled tasks"""
        return self.inspect().scheduled()

    def registered_tasks(self):
        """Get registered tasks"""
        return self.inspect().registered()

    def worker_stats(self):
        """Get worker statistics"""
        return self.inspect().stats()
