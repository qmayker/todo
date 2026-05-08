import logging
from django.utils import timezone
from django.db import transaction
from todo.celery import check_task_status
from scheduler.models import Task

logger = logging.getLogger(__name__)


def check_tasks():
    with transaction.atomic():
        tasks = Task.objects.select_for_update(skip_locked=True).filter(
            status=Task.Status.RECIEVED, start__lte=timezone.now()
        )
        ids = list(tasks.values_list("id", flat=True))
        tasks.update(status=Task.Status.PROCESSING)

    tasks = Task.objects.filter(id__in=ids, status=Task.Status.PROCESSING)
    for task in tasks:
        logger.info(f"{task}")
        check_task_status.apply_async(
            task.task.id, task.task.content_type.id, task.ending
        )
