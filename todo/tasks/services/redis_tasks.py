import logging
from datetime import datetime
from redis import Redis
from todo.celery import check_tasks_status
from scheduler import models, task_statuses
from tasks.models import Task
from .redis_keys import get_task_keys

logger = logging.getLogger(__name__)


def set_task_id(
    r: Redis,
    id: int,
    ct: int,
    eta: datetime,
    task_id: int,
    keys: dict | None = None,
    end: bool = False,
) -> None:
    """Should be under Lock"""
    if not keys:
        keys = get_task_keys(id, ct)
    celery_task = check_tasks_status.apply_async(args=[id, ct, task_id, end], eta=eta)
    task = Task.objects.get(id=task_id)
    models.CeleryTask.objects.create(
        celery_id=celery_task.id,
        start=eta,
        task=task,
        status=task_statuses.Status.RECEIVED,
        ending=end,
    )
    logger.info(f"task {task_id} was scheduled and saved to db")

    r.set(keys["key"], f"{task_id}")
