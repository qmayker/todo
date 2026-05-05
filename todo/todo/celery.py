import os
import redis_lock
from celery import Celery
from celery.utils.log import get_task_logger
from django.db import transaction
from tasks.services import redis_keys


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")
app = Celery("tasks")
logger = get_task_logger(__name__)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(name="check_task_status", bind=True)
def check_task_status(self, id: int, ct: int, end: bool = False):
    from django.contrib.contenttypes.models import ContentType
    from tasks.models import OneTime, RecurringState
    from tasks.services import recurring
    from .redis_client import r

    ct_model = ContentType.objects.get_for_id(ct)
    model = ct_model.model_class()
    keys = redis_keys.get_task_keys(id, ct)
    with redis_lock.Lock(r, keys["lock_key"], expire=20, auto_renewal=True):
        with transaction.atomic():
            try:
                if model is OneTime and not end:
                    ...
                elif model is OneTime and end:
                    ...
                elif model is RecurringState and not end:
                    recurring.start_recurring(model, id, ct, logger)
                elif model is RecurringState and end:
                    recurring.end_recurring(model, id, ct, logger)
            except Exception as e:
                logger.error(f"some error with {model} id {id}", exc_info=e)
