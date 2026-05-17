from django.contrib.contenttypes.models import ContentType
from redis_lock import Lock
from redis import Redis
from datetime import datetime
from logging import Logger
from abc import ABC, abstractmethod
from todo.celery import check_tasks_status, app
from scheduler.models import CeleryTask
from tasks.models import Task
from .types import TaskSchedule
from .redis_keys import get_task_keys


class CeleryService(ABC):
    CONTENT_TYPE_ID: int | None

    def __init__(
        self,
        obj_id: int,
        logger: Logger,
        r: Redis,
        celery_id: str | None = None,
    ):
        self.obj_id = obj_id
        self.logger = logger
        self.r = r
        self.celery_id = celery_id
        self.keys = get_task_keys(self.obj_id, self.get_content_type_id())

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

    def run(self, end: bool):
        self.logger.info(f"run {self.get_model()} {self.obj_id} {end}")
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
                args=[self.obj_id, self.get_content_type_id()],
                eta=schedule.eta,
                end=end,
            )

    def schedule_run(self, eta: datetime):
        with Lock(self.r, self.keys["lock_key"], expire=30, auto_renewal=True):
            self._delete_task()
            self._apply_task(
                args=[self.obj_id, self.get_content_type_id()], eta=eta, end=False
            )

    def _apply_task(self, end: bool, args: list, eta: datetime):
        task = check_tasks_status.apply_async(args=args, eta=eta, kwargs={"end": end})
        CeleryTask.objects.create(
            celery_id=task.id,
            task=self.task,
            start=eta,
            ending=end,
        )
        self.r.set(self.keys["key"], f"{task.id}")

    def _delete_task(self):
        task_id = self.r.get(self.keys["key"])
        if not task_id:
            return
        task_id = task_id.decode()
        if task_id == self.celery_id:
            self.logger.info(f"task {task_id} is the newest")
            return
        self.logger.info(f"revoking task {task_id}")
        app.control.revoke(task_id, terminate=True)

    # TODO
    @property
    def task(self) -> Task:
        obj = self.get_model().objects.get(id=self.obj_id)
        return obj.get_task()
