from django.db import models
from .task_statuses import Status
from .querysets import CeleryTaskQueryset

# Create your models here.


class CeleryTask(models.Model):
    """Celery tasks"""

    celery_id = models.CharField(unique=True)
    task = models.ForeignKey(
        "tasks.Task", related_name="celery", on_delete=models.CASCADE
    )
    start = models.DateTimeField()
    ending = models.BooleanField(default=False)  # if this starting or ending Task
    status = models.CharField(choices=Status)
    objects = CeleryTaskQueryset.as_manager()

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [models.Index(fields=["start"])]
        ordering = ["-start"]

    def __str__(self):
        """Unicode representation of Task."""
        return "Celery task"
