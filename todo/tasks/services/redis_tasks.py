import logging
from redis import Redis
from todo.celery import check_task_status
from scheduler.models import Task as celeryTask
from tasks.models import Task
from .redis_keys import get_task_keys

logger = logging.getLogger(__name__)


def set_task_id(
    r: Redis, id: int, ct: int, eta, keys: dict | None = None, end: bool = False
) -> None:
    if not keys:
        keys = get_task_keys(id, ct)
    celery_task = check_task_status.apply_async(args=[id, ct, end], eta=eta)
    task_id = celery_task.id
    task = Task.objects.get(content_type=ct, object_id=id)
    celeryTask.objects.create(celery_id=task_id, start=eta, task=task)
    logger.info(f"task {task_id} was scheduled and saved to db")
    r.set(keys["key"], f"{task_id}")
