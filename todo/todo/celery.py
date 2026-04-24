import os
from celery import Celery
from datetime import timedelta


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")
app = Celery("tasks")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(name="check_task_status")
def check_task_status():
    from tasks.models import OneTime, Task
    tasks = Task.objects.filter(completed=False, content_type__model='OneTime')
    print(tasks)
    # start writing celery code

app.conf.beat_schedule = {
    "test":{
        "task": 'check_task_status',
        'schedule': timedelta(seconds=60)
    }
}
