from django.db.models import QuerySet
from redis import Redis
from redis_lock import Lock
from logging import Logger
from tasks.models import Task
from todo.celery import app
from .redis_keys import get_task_keys


class TaskServices:
    def __init__(self, logger: Logger, r: Redis):
        self.logger = logger
        self.r = r

    @staticmethod
    def delete_redis_task(r: Redis, keys: dict):
        task_id = r.get(keys["key"])
        if task_id:
            app.control.revoke(task_id.decode(), terminate=True)

    def delete(self, obj: Task):
        keys = get_task_keys(obj.object_id, obj.content_type)
        with Lock(self.r, keys["lock_key"], expire=30):
            self.delete_redis_task(self.r, keys)
            self.logger.info(f"{obj.content_object}")
            obj.content_object.delete()

    def delete_qs(self, qs:QuerySet[Task]):
        for obj in qs:
            self.delete(obj)
