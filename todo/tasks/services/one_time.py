import logging
from django.core.exceptions import ValidationError
from django.db import transaction
from tasks.models import OneTime
from .celery import CeleryService
from .validation import TimeValidation
from .types import TaskSchedule

logger = logging.getLogger(__name__)


class OneTimeValidation(TimeValidation):
    FIELDS = {"start": "starts_at", "end": "expires_at", "complete": "completed"}

    def __init__(self, cd, changed_data: list[str], logger):
        super().__init__(cd, changed_data, logger, self.FIELDS)

    def validate_time(self):
        self.logger.info(f"{self.changed_data} {self.cd}")
        if (
            self.end_name not in self.changed_data
            and self.start_name not in self.changed_data
        ):
            return
        self.time_validation()

    def validate_starts_at(self):
        if self.start_name not in self.changed_data:
            return
        if not self.start:
            return
        if self.start < self.now:
            raise ValidationError("Starting time can not be in past")
        return

    def validate_expires_at(self):
        if self.end_name not in self.changed_data:
            return
        if not self.end:
            return
        if self.end <= self.now:
            raise ValidationError("Expiring time can not be in past")
        return

    def validate(self):
        self.validate_starts_at()
        self.validate_expires_at()
        self.validate_time()


class OneTimeServices(CeleryService):
    CONTENT_TYPE_ID = None
    start_name = OneTimeValidation.FIELDS.get("start")
    completed_name = OneTimeValidation.FIELDS.get("complete")

    def __init__(self, obj_id: int, *args, **kwargs):
        super().__init__(obj_id=obj_id, *args, **kwargs)

    @classmethod
    def save(cls, obj: OneTime, cd: dict, changed_data: list, change:bool) -> TaskSchedule:
        if not changed_data and change:
            return TaskSchedule(eta=None, schedule=None)
        if set(changed_data) == {cls.completed_name}:
            obj.save()
            return TaskSchedule(eta=None, schedule=False)
        starts_at = cd.get(cls.start_name)
        obj.starts_at = starts_at
        obj.started = False
        obj.expired = False
        obj.completed = False
        obj.save()
        return TaskSchedule(eta=starts_at, schedule=True)

    
    @transaction.atomic
    def start(self):
        task = self.get_model().objects.select_for_update().get(id=self.obj_id)
        task.started = True
        task.save()

        if not task.expires_at:
            return TaskSchedule(eta=None, schedule=False)

        return TaskSchedule(eta=task.expires_at, schedule=True)

    def end(self):
        task = self.get_model().objects.filter(id=self.obj_id)
        task.update(expired=True)
        return TaskSchedule(eta=None, schedule=False)

    @staticmethod
    def get_model() -> OneTime:
        return OneTime
