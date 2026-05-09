import logging
from django.utils import timezone
from django.db import transaction
from celery import shared_task
from todo.celery import check_task_status
from scheduler.models import CeleryTask

logger = logging.getLogger(__name__)


@shared_task()
def check_tasks():
    with transaction.atomic():
        tasks = CeleryTask.objects.select_for_update(skip_locked=True).filter(
            status=CeleryTask.Status.RECIEVED, # TODO or error
            start__lte=timezone.now(),
        )
        ids = list(tasks.values_list("id", flat=True))
        tasks.update(status=CeleryTask.Status.PROCESSING)

    tasks = CeleryTask.objects.filter(
        id__in=ids, status=CeleryTask.Status.PROCESSING
    ).select_related("task")
    for task in tasks:
        # TODO add lock, if need
        logger.info(f"{task}")
        check_task_status.apply_async(
            args=[task.task.object_id, task.task.content_type.id, task.ending, task.celery_id]
        )
