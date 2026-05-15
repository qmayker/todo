from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from logging import Logger
from abc import ABC, abstractmethod
from tasks.models import OneTime, RecurringState
from todo.celery import check_tasks_status
from .types import TaskSchedule


class CeleryService(ABC):
    CONTENT_TYPE_ID: int | None

    def __init__(self, obj: OneTime | RecurringState, logger: Logger):
        self.obj = obj
        self.logger = logger

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
    def get_by_id(cls, id: int, logger: Logger):
        obj = cls.get_model().objects.get(id=id)
        return cls(obj, logger)

    def run(self, end: bool):
        self.logger.info(f"run {self.obj} {end}")
        if end:
            schedule = self.end()
            end = False
        else:
            schedule = self.start()
            end = True
        if not schedule.schedule:
            return
        check_tasks_status.apply_async(
            args=[self.obj.id, self.get_content_type_id(), end], eta=schedule.eta
        )

    def schedule_run(self, eta: datetime):
        check_tasks_status.apply_async(
            args=[self.obj.id, self.get_content_type_id(), False], eta=eta
        )
