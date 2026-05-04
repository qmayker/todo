import logging
from redis_lock import Lock
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from tasks.models import Recurring, RecurringState, RecurringStateHistory
from todo.celery import check_task_status, app
from todo.redis_client import r
from .redis_keys import get_task_keys
from .redis_tasks import set_task_id

logger = logging.getLogger(__name__)


@transaction.atomic()
def create_recurring_state(recurring: Recurring, changed_data: list[str]):
    logger.info(f"{changed_data}")
    if not changed_data:
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

    def schedule_task():
        id = state.id
        ct = ContentType.objects.get_for_model(state).id
        keys = get_task_keys(id, ct)
        with Lock(r, keys["lock_key"], expire=10):
            task_id = r.get(keys["key"])
            logger.debug(f"{keys['key']} {task_id}")
            if task_id:
                logger.debug(f"Deleting task {task_id}")
                app.control.revoke(task_id.decode())
            set_task_id(r=r, id=id, ct=ct, eta=state.next_time, keys=keys)

    transaction.on_commit(schedule_task)


def start_recurring(model: type[RecurringState], id: int, ct: int, logger):
    logger.debug(f"Model {model} id {id} starting")
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
    logger.debug(f"Model {model} id {id} started")
    keys = get_task_keys(id, ct)
    task = check_task_status.apply_async(
        args=[id, ct, True], eta=recurring_state.ends_at
    )
    r.set(keys["key"], task.id)


def end_recurring(model: type[RecurringState], id: int, ct: int, logger):
    logger.debug(f"model {model} id {id} ending")
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
    logger.debug(f"model {model} id {id} ended")
    keys = get_task_keys(id, ct)
    task = check_task_status.apply_async(args=[id, ct], eta=recurring_state.next_time)
    r.set(keys["key"], task.id)


# todo - дозволити оновлювати таск, при цьому не перевіряючи час
