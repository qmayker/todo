from django.db import models

# Create your models here.


class Task(models.Model):
    """Celery tasks"""
    class Status(models.TextChoices):
        RECIEVED = "RC", "Recieved"
        REVOKED = "RV", "Revoked"
        COMPLETED = 'CM', 'Completed'
        RUNNING = 'RN', 'Running',
        ERROR = 'ERR', 'Error'

    celery_id = models.CharField(unique=True)
    task = models.ForeignKey('tasks.Task', related_name='celery', on_delete=models.CASCADE)
    start = models.DateTimeField()
    ending = models.BooleanField(default=False)
    status = models.CharField(choices=Status)

    class Meta:

        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [models.Index(fields=["start"])]

    def __str__(self):
        """Unicode representation of Task."""
        return "Celery task"
