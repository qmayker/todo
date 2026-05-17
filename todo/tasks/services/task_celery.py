import logging
from todo.redis_client import r
from todo.celery import app


logger = logging.getLogger(__name__)


def delete_task(keys: dict, terminate: bool = False):
    task_id = r.get(keys["key"])
    logger.debug(f"{keys['key']} {task_id}")
    if task_id:
        logger.debug(f"Deleting task {task_id}")
        app.control.revoke(task_id.decode(), terminate=terminate)
