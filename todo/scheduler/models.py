from django.db import models

# Create your models here.


class CeleryTask(models.Model):
    """Celery tasks"""

    class Status(models.TextChoices):
        RECIEVED = "RC", "Recieved"  # sent to celery
        PROCESSING = "PR", "Processing"  # check_tasks is working with this task
        RUNNING = "RN", "Running"  # check_task_status started
        COMPLETED = (
            "CN",
            "Completed",  # check_task_status completed
        )
        ERROR = "ERR", "Error"  # check_task_status caused an error

    celery_id = models.CharField(unique=True)
    task = models.ForeignKey(
        "tasks.Task", related_name="celery", on_delete=models.CASCADE
    )
    start = models.DateTimeField()
    ending = models.BooleanField(default=False)  # if this starting or ending Task
    status = models.CharField(choices=Status)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [models.Index(fields=["start"])]
        ordering = ["-start"]

    def __str__(self):
        """Unicode representation of Task."""
        return "Celery task"
