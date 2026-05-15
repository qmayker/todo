import logging
from django.db import transaction
from django.utils import timezone
from tasks.models import RecurringState, RecurringStateHistory
from .celery import CeleryService
from .types import TaskSchedule


class RecurringStateServices(CeleryService):
    CONTENT_TYPE_ID = None

    def __init__(self, obj: RecurringState, logger: logging.Logger):
        super().__init__(obj, logger=logger)
        self.obj: RecurringState

    @transaction.atomic
    def end(self):
        self.obj.is_running = False
        RecurringStateHistory.objects.create(
            completed=self.obj.completed,
            state=self.obj,
            started_at=self.obj.last_run_at,
            ended_at=self.obj.ends_at,
        )
        self.obj.save()
        return TaskSchedule(eta=self.obj.next_time, schedule=True)

    def start(self):
        self.obj.is_running = True
        self.obj.completed = False
        now = timezone.now()
        self.obj.last_run_at = now
        duration = self.obj.recurring.duration_time
        ends_at = now + duration
        self.obj.ends_at = ends_at
        self.obj.next_time = ends_at + self.obj.recurring.interval
        self.obj.save()
        return TaskSchedule(eta=self.obj.ends_at, schedule=True)

    @staticmethod
    def get_model() -> RecurringState:
        return RecurringState
