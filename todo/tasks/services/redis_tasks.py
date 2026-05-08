import logging
from redis import Redis
from todo.celery import check_task_status
from .redis_keys import get_task_keys

logger = logging.getLogger(__name__)


def set_task_id(
    r: Redis, id: int, ct: int, eta, keys: dict | None = None, end: bool = False
) -> None:
    if not keys:
        keys = get_task_keys(id, ct)
    task = check_task_status.apply_async(args=[id, ct, end], eta=eta)
    task_id = task.id
    logger.info(f"task {task_id} was scheduled")
    r.set(keys["key"], f"{task_id}")
