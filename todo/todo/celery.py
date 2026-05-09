import os
import redis_lock
from datetime import timedelta
from celery import Celery
from celery.utils.log import get_task_logger
from tasks.services import redis_keys


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")
app = Celery("tasks")
logger = get_task_logger(__name__)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(name="check_task_status", bind=True)
def check_task_status(
    self, id: int, ct: int, end: bool = False, celery_id: str | None = None
):
    from django.contrib.contenttypes.models import ContentType
    from scheduler.models import CeleryTask
    from tasks.models import OneTime, RecurringState
    from tasks.services import recurring, one_time
    from .redis_client import r

    ct_model = ContentType.objects.get_for_id(ct)
    model = ct_model.model_class()
    if not celery_id:
        status = CeleryTask.Status.RECIEVED
        celery_id = self.request.id
    else:
        status = CeleryTask.Status.PROCESSING

    keys = redis_keys.get_task_keys(id, ct, end=end)
    with redis_lock.Lock(r, keys["lock_key"], expire=40, auto_renewal=True):
        logger.info(f"task {celery_id} started")
        updated = CeleryTask.objects.filter(celery_id=celery_id, status=status).update(
            status=CeleryTask.Status.RUNNING
        )
        if updated == 0:
            return
        try:
            if model is OneTime:
                if not end:
                    one_time.start_one_time(id, ct)
                else:
                    one_time.end_one_time(id)
            elif model is RecurringState:
                if not end:
                    recurring.start_recurring(model, id, ct, logger)
                else:
                    recurring.end_recurring(model, id, ct, logger)
            CeleryTask.objects.filter(
                celery_id=celery_id, status=CeleryTask.Status.RUNNING
            ).update(status=CeleryTask.Status.COMPLETED)
        except Exception:
            CeleryTask.objects.filter(
                celery_id=celery_id, status=CeleryTask.Status.RUNNING
            ).update(status=CeleryTask.Status.ERROR)
            logger.exception(f"some error with {model} id {id}")

    logger.debug(f"task for model {model} id {id} end {end} was finished")
    # TODO change Task status


app.conf.beat_schedule = {
    "check_tasks": {
        "task": "scheduler.services.tasks.check_tasks",
        "schedule": timedelta(seconds=30),
    }
}
