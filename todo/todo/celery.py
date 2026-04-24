import os
from celery import Celery
from datetime import timedelta
from django.utils import timezone


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")
app = Celery("tasks")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(name="check_task_status")
def check_task_status():
    from tasks.models import Task, OneTime

    try:
        onetime_tasks = Task.objects.filter(
            completed=False,
            content_type__model="onetime",
            onetime__expired=False,
            onetime__expires_at__lte=timezone.now(),
        )
        onetime_objects = OneTime.objects.filter(
            task__id__in=onetime_tasks.values_list("id", flat=True)
        )
        onetime_objects.update(expired=True)
    except Task.DoesNotExist:
        return


app.conf.beat_schedule = {
    "test": {"task": "check_task_status", "schedule": timedelta(seconds=60)}
}
