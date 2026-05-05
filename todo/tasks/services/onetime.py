from django.core.exceptions import ValidationError
from django.utils import timezone
from tasks.models import OneTime
from .task_celery import schedule_first_task


def validate_time(cd: dict, changed_data: dict):
    if not changed_data:
        return cd
    if "expires_at" not in changed_data:
        return cd
    expires_at = cd.get("expires_at")
    if not expires_at:
        return cd
    if expires_at <= timezone.now():
        raise ValidationError({"expires_at": "Expiring time can not be in past"})
    return cd


def start_one_time(onetime: OneTime):
    if not onetime.expires_at:
        return
    schedule_first_task(OneTime, onetime.expires_at)


def end_one_time(onetime: OneTime):
    OneTime.objects.filter(id=onetime.id).update(expired=True)
