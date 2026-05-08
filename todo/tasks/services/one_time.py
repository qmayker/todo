import logging
from django.core.exceptions import ValidationError
from django.utils import timezone
from tasks.models import OneTime
from .task_celery import schedule_first_task, schedule_task
from .validation import time_validation

logger = logging.getLogger(__name__)


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


def validate_time(cd: dict, changed_data: list):
    if "expires_at" not in changed_data and "starts_at" not in changed_data:
        return
    expires_at = cd.get("expires_at")
    starts_at = cd.get("starts_at")
    time_validation(starts_at, expires_at, changed_data)


def validate_starts_at(cleaned_data: dict, changed_data: dict):
    starts_at = cleaned_data.get("starts_at")
    if "starts_at" not in changed_data:
        return starts_at
    if not starts_at:
        return starts_at
    if starts_at <= timezone.now():
        raise ValidationError("Starting time can not be in past")
    return starts_at


def validate_expires_at(cleaned_data: dict, changed_data: dict):
    expires_at = cleaned_data.get("expires_at")
    if "expires_at" not in changed_data:
        return expires_at
    if not expires_at:
        return expires_at
    if expires_at <= timezone.now():
        raise ValidationError("Expiring time can not be in past")
    return expires_at


def validate(cleaned_data: dict, changed_data: dict):
    validate_time(cleaned_data, changed_data)
    validate_starts_at(cleaned_data, changed_data)
    validate_expires_at(cleaned_data, changed_data)
