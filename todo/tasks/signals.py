from redis_lock import Lock
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .services.task_celery import delete_task
from .services.redis_keys import get_delete_by_object
from todo.redis_client import r
from .models import Task


@receiver(post_delete, sender=Task)
def task_delete_hander(instance: Task, *args, **kwargs):
    obj = instance.content_object
    if obj:
        keys = get_delete_by_object(obj)
        with Lock(r, keys["lock_key"], expire=10):
            delete_task(keys)
        instance.content_object.delete()

    # remake with manually deleting
