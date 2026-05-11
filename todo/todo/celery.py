import os
import redis_lock
from datetime import timedelta
from celery import Celery
from celery.utils.log import get_task_logger
from tasks.services import redis_keys
from scheduler.task_statuses import Status


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")
app = Celery("tasks")
logger = get_task_logger(__name__)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(name="check_task_status", bind=True)
def check_task_status(
    self,
    id: int,
    ct: int,
    task_id: int,
    end: bool = False,
    celery_id: str | None = None,
):
    from django.contrib.contenttypes.models import ContentType
    from scheduler.models import CeleryTask
    from tasks.models import OneTime, RecurringState
    from tasks.services import recurring, one_time
    from .redis_client import r

    ct_model = ContentType.objects.get_for_id(ct)
    model = ct_model.model_class()
    if not celery_id:
        status = Status.RECEIVED
        celery_id = self.request.id
    else:
        status = Status.PROCESSING
    keys = redis_keys.get_task_keys(id, ct, end=end)

    with redis_lock.Lock(r, keys["lock_key"], expire=40, auto_renewal=True):
        logger.info(f"task {celery_id} started")
        updated = CeleryTask.objects.start_running(celery_id=celery_id, status=status)
        if updated == 0:
            return
        try:
            if model is OneTime:
                if not end:
                    one_time.start_one_time(id, ct, task_id)
                else:
                    one_time.end_one_time(id)
            elif model is RecurringState:
                if not end:
                    recurring.start_recurring(
                        id=id, ct_id=ct, task_id=task_id, logger=logger
                    )
                else:
                    recurring.end_recurring(
                        id=id, ct_id=ct, task_id=task_id, logger=logger
                    )
            CeleryTask.objects.update_completed(celery_id)
        except Exception:
            CeleryTask.objects.update_error(celery_id)
            logger.exception(f"some error with {model} id {id}")

    logger.info(f"task for model {model} id {id} end {end} was finished")


app.conf.beat_schedule = {
    "check_tasks": {
        "task": "scheduler.services.tasks.check_tasks",
        "schedule": timedelta(seconds=30),
    }
}
