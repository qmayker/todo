from redis import Redis
from todo.celery import check_task_status
from .redis_keys import get_task_keys


def set_task_id(
    r: Redis, id: int, ct: int, eta, keys: dict | None = None, end: bool = False
) -> None:
    if not keys:
        keys = get_task_keys(id, ct)
    task = check_task_status.apply_async(args=[id, ct, end], eta=eta)
    r.set(keys["key"], f"{task.id}")
