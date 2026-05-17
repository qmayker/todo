from django.db import transaction
from django.utils import timezone
from tasks.models import RecurringState, RecurringStateHistory
from .types import TaskSchedule


class RecurringStateServices():
    def __init__(self, obj_id:int):
        self.obj_id = obj_id

    @transaction.atomic
    def end(self):
        task = (
            self.get_model()
            .objects.select_for_update()
            .get(id=self.obj_id, is_running=True)
        )
        task.is_running = False
        task.save()
        RecurringStateHistory.objects.create(
            completed=task.completed,
            state=task,
            started_at=task.last_run_at,
            ended_at=task.ends_at,
        )
        return TaskSchedule(eta=task.next_time, schedule=True)

    @transaction.atomic
    def start(self):
        task = (
            self.get_model()
            .objects.select_for_update()
            .get(id=self.obj_id, is_running=False)
        )
        duration = task.recurring.duration_time
        now = timezone.now()
        ends_at = now + duration
        next_time = ends_at + task.recurring.interval

        task.is_running = True
        task.completed = False
        task.last_run_at = now
        task.ends_at = ends_at
        task.next_time = next_time
        task.save()
        return TaskSchedule(eta=ends_at, schedule=True)

    @staticmethod
    def get_model() -> RecurringState:
        return RecurringState
