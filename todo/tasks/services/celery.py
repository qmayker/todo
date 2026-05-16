from django.contrib.contenttypes.models import ContentType
from redis_lock import Lock
from redis import Redis
from datetime import datetime
from logging import Logger
from abc import ABC, abstractmethod
from tasks.models import OneTime, RecurringState
from todo.celery import check_tasks_status, app
from .types import TaskSchedule
from .redis_keys import get_task_keys


class CeleryService(ABC):
    CONTENT_TYPE_ID: int | None

    def __init__(
        self,
        obj: OneTime | RecurringState,
        logger: Logger,
        r: Redis,
        task_id: str | None = None,
    ):
        self.obj = obj
        self.logger = logger
        self.r = r
        self.task_id = task_id
        self.keys = get_task_keys(self.obj.id, self.get_content_type_id())

    @abstractmethod
    def start(self) -> TaskSchedule: ...

    @abstractmethod
    def end(self) -> TaskSchedule: ...

    @classmethod
    def get_content_type_id(cls) -> int:
        if not cls.CONTENT_TYPE_ID:
            ct = ContentType.objects.get_for_model(cls.get_model())
            cls.CONTENT_TYPE_ID = ct.id
        return cls.CONTENT_TYPE_ID

    @staticmethod
    @abstractmethod
    def get_model(): ...

    @classmethod
    def get_by_id(cls, id: int, *args, **kwargs):
        obj = cls.get_model().objects.get(id=id)
        return cls(obj, *args, **kwargs)

    def run(self, end: bool):
        self.logger.info(f"run {self.obj} {end}")
        with Lock(self.r, self.keys["lock_key"], expire=30, auto_renewal=True):
            self._delete_task()
            if end:
                schedule = self.end()
                end = False
            else:
                schedule = self.start()
                end = True
            if not schedule.schedule:
                return
            self._apply_task(
                args=[self.obj.id, self.get_content_type_id(), end], eta=schedule.eta
            )

    def schedule_run(self, eta: datetime):
        with Lock(self.r, self.keys["lock_key"], expire=30, auto_renewal=True):
            self._delete_task()
            self._apply_task(
                args=[self.obj.id, self.get_content_type_id(), False], eta=eta
            )

    def _apply_task(self, args: list, eta: datetime):
        task = check_tasks_status.apply_async(args=args, eta=eta)
        self.r.set(self.keys["key"], f"{task.id}")

    def _delete_task(self):
        task_id = self.r.get(self.keys["key"]).decode()
        self.logger.info(f'{task_id}, self - {self.task_id}')
        if task_id and task_id != self.task_id:
            app.control.revoke(task_id, terminate=True)
