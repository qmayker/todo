from celery import Celery
from tasks.models import OneTime, Task

app = Celery("tasks", broker="")


@app.task()
def check_task_status():
    OneTime.objects.filter(task__completed=False, )