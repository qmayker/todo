import logging
from django.core.exceptions import ValidationError
from django.utils import timezone
from tasks.models import OneTime
from todo.celery import check_tasks_status
from .celery import CeleryService
from .validation import TimeValidation
from .types import TaskSchedule

logger = logging.getLogger(__name__)


class OneTimeServices(CeleryService):
    CONTENT_TYPE_ID = None

    def __init__(self, obj: OneTime, logger: logging.Logger):
        super().__init__(obj, logger)
        self.obj: OneTime
        self.start_name = OneTimeValidation.FIELDS.get("start")
        self.completed_name = OneTimeValidation.FIELDS.get("complete")

    def save(self, cd: dict, changed_data: list) -> TaskSchedule:
        if set(changed_data) == {self.completed_name}:
            self.obj.save()
            return TaskSchedule(eta=None, schedule=False)
        self.obj.starts_at = cd.get(self.start_name)
        self.obj.started = False
        self.obj.expired = False
        self.obj.completed = False
        self.obj.save()
        return TaskSchedule(eta=self.obj.starts_at, schedule=True)

    def start(self):
        self.obj.started = True
        self.obj.save(update_fields=["started"])
        return TaskSchedule(eta=self.obj.expires_at, schedule=True)

    def end(self):
        self.obj.expired = True
        self.obj.save(update_fields=["expired"])
        return TaskSchedule(eta=None, schedule=False)

    @staticmethod
    def get_model() -> OneTime:
        return OneTime


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
