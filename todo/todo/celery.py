import os
import redis_lock
from datetime import timedelta
from celery import Celery
from celery.utils.log import get_task_logger
from scheduler.task_statuses import Status


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")
app = Celery("tasks")
logger = get_task_logger(__name__)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


# TODO task revokes itself. FIX
@app.task(name="check_task_status", bind=True)
def check_tasks_status(self, id: int, ct_id: int, end: bool):
    from tasks.services import one_time, recurring_state
    from scheduler.models import CeleryTask
    from .redis_client import r

    try:
        if ct_id is one_time.OneTimeServices.get_content_type_id():
            service = one_time.OneTimeServices(
                id, logger=logger, r=r, task_id=self.request.id
            )
        else:
            service = recurring_state.RecurringStateServices(
                id=id, logger=logger, r=r, task_id=self.request.id
            )
        service.run(end=end)
    except Exception:
        try:
            logger.error(f"Some error with service={service}, id={id}")
        except UnboundLocalError:
            logger.error(f"Could not load service for ct_id={ct_id}, id={id}")


# app.conf.beat_schedule = {
#     "check_tasks": {
#         "task": "scheduler.services.tasks.check_tasks",
#         "schedule": timedelta(seconds=30),
#     }
# }
