import os
from datetime import timedelta
from redis_lock import Lock, NotAcquired
from celery import Celery
from celery.utils.log import get_task_logger
from scheduler.task_statuses import Status


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")
app = Celery("tasks")
logger = get_task_logger(__name__)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(name="check_task_status", bind=True)
def check_tasks_status(
    self, id: int, ct_id: int, end: bool, celery_id: str | None = None
):
    from scheduler.models import CeleryTask
    from tasks.services import one_time, recurring_state, recurring
    from .redis_client import r

    if not celery_id:
        celery_id = self.request.id
        filter_status = Status.RECEIVED
    else:
        filter_status = Status.PROCESSING
    try:
        with Lock(r, celery_id, expire=30, auto_renewal=True, blocking=False):
            update_res = CeleryTask.objects.start_running(celery_id, filter_status)
            logger.info(f"{update_res}")
            if update_res == 0:
                return
            if ct_id is one_time.OneTimeServices.get_content_type_id():
                service = one_time.OneTimeServices(
                    obj_id=id, logger=logger, r=r, celery_id=self.request.id
                )
            else:
                recurring_service = recurring.RecurringServices.get_by_id(id)
                service = recurring_state.RecurringStateServices(
                    obj_id=recurring_service.get_state_id(),
                    logger=logger,
                    r=r,
                    celery_id=self.request.id,
                )
            service.run(end=end)
            CeleryTask.objects.update_completed(celery_id)
    except NotAcquired:
        CeleryTask.objects.update_completed(celery_id)
        logger.info(f"Lock for {celery_id}, id={id}, ct_id={ct_id} is already acquired")
    except Exception:
        CeleryTask.objects.update_error(celery_id)
        try:
            logger.exception(f"Some error with service={service}, id={id}")
        except UnboundLocalError:
            logger.exception(f"Could not load service for ct_id={ct_id}, id={id}")


app.conf.beat_schedule = {
    "check_tasks": {
        "task": "scheduler.services.tasks.check_tasks",
        "schedule": timedelta(seconds=30),
    }
}
