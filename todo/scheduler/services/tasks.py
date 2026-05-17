import logging
from django.utils import timezone
from django.db import transaction
from celery import shared_task
from todo.celery import check_tasks_status
from scheduler.models import CeleryTask
from scheduler.task_statuses import Status

logger = logging.getLogger(__name__)


@shared_task()
def check_tasks():
    with transaction.atomic():
        tasks = CeleryTask.objects.select_for_update(skip_locked=True).filter(
            status__in=[Status.RECEIVED, Status.ERROR],
            start__lte=timezone.now(),
        )
        ids = list(tasks.values_list("id", flat=True))
        tasks.update(status=Status.PROCESSING)

    tasks = CeleryTask.objects.filter(
        id__in=ids, status=Status.PROCESSING
    ).select_related("task")
    for task in tasks:
        check_tasks_status.delay(
            id=task.task.object_id,
            ct_id=task.task.content_type.id,
            end=task.ending,
            celery_id=task.celery_id,
        )
