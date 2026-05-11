from django.db import models

class Status(models.TextChoices):
        RECEIVED = "RC", "Received"  # sent to celery
        PROCESSING = "PR", "Processing"  # check_tasks is working with this task
        RUNNING = "RN", "Running"  # check_task_status started
        COMPLETED = (
            "CN",
            "Completed",  # check_task_status completed
        )
        ERROR = "ERR", "Error"  # check_task_status caused an error