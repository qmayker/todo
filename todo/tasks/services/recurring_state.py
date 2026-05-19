from django.db import transaction
from django.utils import timezone
from tasks.models import RecurringState, RecurringStateHistory, Task
from .types import TaskSchedule


class RecurringStateServices:
    def __init__(self, obj_id: int):
        self.obj_id = obj_id

    @transaction.atomic
    def end(self, task: Task):
        state = (
            self.get_model()
            .objects.select_for_update()
            .get(id=self.obj_id, is_running=True)
        )
        state.is_running = False
        state.save()
        RecurringStateHistory.objects.create(
            completed=state.completed,
            state=state,
            started_at=state.last_run_at,
            ended_at=state.ends_at,
            task=task,
            task_name=task.name,
        )
        return TaskSchedule(eta=state.next_time, schedule=True)

    @transaction.atomic
    def start(self):
        state = (
            self.get_model()
            .objects.select_for_update()
            .get(id=self.obj_id, is_running=False)
        )
        duration = state.recurring.duration_time
        now = timezone.now()
        ends_at = now + duration
        next_time = ends_at + state.recurring.interval

        state.is_running = True
        state.completed = False
        state.last_run_at = now
        state.ends_at = ends_at
        state.next_time = next_time
        state.save()
        return TaskSchedule(eta=ends_at, schedule=True)

    @staticmethod
    def get_model() -> RecurringState:
        return RecurringState
