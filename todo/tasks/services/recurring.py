import logging
from redis_lock import Lock
from datetime import timedelta
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from tasks.models import Recurring, RecurringState, RecurringStateHistory
from todo.celery import check_task_status, app
from todo.redis_client import r

logger = logging.getLogger(__name__)


@transaction.atomic()
def create_recurring_state(recurring: Recurring):

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

    def schedule_task():
        state_id = state.id
        ct_id = ContentType.objects.get_for_model(state).id
        key = f"task:{state_id}:{ct_id}"
        lock_key = f"lock:{state_id}:{ct_id}"
        with Lock(r, lock_key, expire=10):
            task_id = r.get(key)
            logger.info(f"{key} {task_id}")
            if task_id:
                logger.info(f"Deleting task {task_id}")
                app.control.revoke(task_id.decode())
            task = check_task_status.apply_async(
                args=[state_id, ct_id], eta=state.next_time
            )
            r.set(key, f"{task.id}")

    transaction.on_commit(schedule_task)


def start_recurring(model: type[RecurringState], id: int, ct: int, logger):
    logger.info(f"Model {model} id {id} starting")
    recurring_state = model.objects.select_for_update().get(id=id, is_running=False)
    duration = recurring_state.recurring.duration_time
    last_run = timezone.now()
    ends_at = duration + last_run
    recurring_state.is_running = True
    recurring_state.last_run_at = last_run
    recurring_state.ends_at = ends_at
    recurring_state.next_time = ends_at + timedelta(
        days=recurring_state.recurring.interval
    )
    recurring_state.save(
        update_fields=[
            "is_running",
            "last_run_at",
            "ends_at",
            "next_time",
        ]
    )
    logger.info(f"Model {model} id {id} started")
    check_task_status.apply_async(args=[id, ct, True], eta=recurring_state.ends_at)


def end_recurring(model: type[RecurringState], id: int, ct: int, logger):
    logger.info(f"model {model} id {id} ending")
    recurring_state = RecurringState.objects.select_for_update().get(
        id=id, is_running=True
    )
    recurring_state.is_running = False
    recurring_state.save(update_fields=["is_running"])
    RecurringStateHistory.objects.create(
        state=recurring_state,
        completed=recurring_state.completed,
        started_at=recurring_state.last_run_at,
        ends_at=recurring_state.ends_at,
    )
    logger.info(f"model {model} id {id} ended")
    key = f"task:{id}:{ct}"
    lock_key = f"lock:{id}:{ct}"
    with Lock(r, lock_key, expire=10):
        res = check_task_status.apply_async(args=[id, ct], eta=recurring_state.next_time)
        r.set(key, res.id)


# todo - дозволити оновлювати таск, при цьому не перевіряючи час
