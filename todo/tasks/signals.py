from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Task


@receiver(post_delete, sender=Task)
def task_delete_hander(instance: Task, *args, **kwargs):
    obj = instance.content_object
    if obj:
        instance.content_object.delete()
