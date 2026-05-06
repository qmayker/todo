import logging
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from tasks.models import Recurring, RecurringState, RecurringStateHistory
from .task_celery import schedule_first_task, schedule_task


logger = logging.getLogger(__name__)


@transaction.atomic()
def create_recurring_state(
    recurring: Recurring, changed_data: list[str], change: bool = True
):

    logger.info(f"{changed_data}")
    if not changed_data and change:
        return
    duration_time = recurring.end_time - recurring.start_time
    recurring.duration_time = duration_time
    recurring.save()
    update_res = RecurringState.objects.update_or_create(
        recurring=recurring,
        defaults={
            "next_time": recurring.start_time,
            "ends_at": recurring.start_time + duration_time,
        },
    )
    state = update_res[0]

    def schedule_task_on_commit():
        schedule_first_task(state, state.next_time)

    transaction.on_commit()


@transaction.atomic
def start_recurring(model: type[RecurringState], id: int, ct_id: int, logger):
    logger.info(f"Model {model} id {id} starting")
    recurring_state = model.objects.select_for_update().get(id=id, is_running=False)
    duration = recurring_state.recurring.duration_time
    last_run = timezone.now()
    ends_at = duration + last_run
    recurring_state.is_running = True
    recurring_state.last_run_at = last_run
    recurring_state.ends_at = ends_at
    recurring_state.next_time = ends_at + recurring_state.recurring.interval
    recurring_state.save(
        update_fields=[
            "is_running",
            "last_run_at",
            "ends_at",
            "next_time",
        ]
    )
    logger.info(f"Model {model} id {id} started")

    def schedule_task_on_commit():
        schedule_task(id, ct_id, eta=recurring_state.next_time, end=True)

    transaction.on_commit(schedule_task_on_commit)
    logger.info(f"Model {model} id {id} end was scheduled")


@transaction.atomic
def end_recurring(model: type[RecurringState], id: int, ct_id: int, logger):
    logger.info(f"model {model} id {id} ending")
    recurring_state = RecurringState.objects.select_for_update().get(
        id=id, is_running=True
    )
    recurring_state.is_running = False
    recurring_state.completed = False
    recurring_state.save(update_fields=["is_running"])
    RecurringStateHistory.objects.create(
        state=recurring_state,
        completed=recurring_state.completed,
        started_at=recurring_state.last_run_at,
        ended_at=recurring_state.ends_at,
    )
    logger.info(f"model {model} id {id} ended")

    def schedule_task_on_commit():
        schedule_task(id, ct_id, eta=recurring_state.next_time)

    transaction.on_commit(schedule_task_on_commit)

    logger.info(f"Model {model} id {id} start was scheduled")


def validate_time(cleaned_data: dict, changed_data: dict):
    if not changed_data:
        return cleaned_data
    start_time = cleaned_data.get("start_time")
    end_time = cleaned_data.get("end_time")
    if "end_time" and "start_time" not in changed_data:
        return cleaned_data
    if start_time and start_time < timezone.now():
        raise ValidationError({"start_time": "Must be in future, not past"})
    if end_time <= start_time:
        raise ValidationError(
            {"end_time": "End time cannot be earlier than start time"}
        )
