import logging
from datetime import datetime
from redis_lock import Lock
from django.contrib.contenttypes.models import ContentType
from todo.redis_client import r
from todo.celery import app
from .redis_tasks import set_task_id
from .redis_keys import get_task_keys


logger = logging.getLogger(__name__)


def schedule_first_task(obj, eta: datetime):
    id = obj.id
    ct_id = ContentType.objects.get_for_model(obj).id
    keys = get_task_keys(id, ct_id)
    with Lock(r, keys["lock_key"], expire=10):
        task_id = r.get(keys["key"])
        logger.debug(f"{keys['key']} {task_id}")
        if task_id:
            logger.debug(f"Deleting task {task_id}")
            app.control.revoke(task_id.decode())
        set_task_id(r=r, id=id, ct=ct_id, eta=eta, keys=keys)


def schedule_task(id: int, ct_id: int, eta: datetime, end: bool = False):
    """should be under redis_lock"""
    keys = get_task_keys(id, ct_id, end=end)
    set_task_id(r, id, ct_id, eta, keys=keys, end=end)
