import logging
from django.core.exceptions import ValidationError
from tasks.models import OneTime
from .task_celery import schedule_first_task, schedule_task

logger = logging.getLogger(__name__)


def validate_time(cd: dict, changed_data: list):
    if not changed_data:
        return cd
    if "expires_at" not in changed_data and "starts_at" not in changed_data:
        return cd
    logger.info(f"{cd}")
    expires_at = cd.get("expires_at")
    starts_at = cd.get("starts_at")
    if starts_at >= expires_at:
        raise ValidationError(
            {
                "expires_at": "Must be later than start_at. Can not be earlier or at the same time"
            }
        )
    return cd


def start_first_one_time(onetime: OneTime):
    logger.info(f"{onetime.started}")
    if onetime.starts_at:
        eta = onetime.starts_at
    else:
        eta = None

    schedule_first_task(onetime, eta)


def start_one_time(id: int, ct_id: int):
    qs = OneTime.objects.filter(id=id, started=False)
    onetime = qs.first()
    qs.update(started=True)
    logger.info(f"{OneTime.objects.filter(id=id)}")
    if not onetime:
        return
    if onetime.expires_at:
        schedule_task(id, ct_id, onetime.expires_at, end=True)


def end_one_time(id: int):
    OneTime.objects.filter(id=id).update(expired=True, started=False)
