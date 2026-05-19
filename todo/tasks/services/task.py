from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import render
from redis import Redis
from redis_lock import Lock
from logging import Logger
from tasks.models import Task
from todo.celery import app
from .redis_keys import get_task_keys


class TaskServices:
    def __init__(self, logger: Logger, r: Redis):
        self.logger = logger
        self.r = r

    @staticmethod
    def delete_redis_task(r: Redis, keys: dict):
        task_id = r.get(keys["key"])
        if task_id:
            app.control.revoke(task_id.decode(), terminate=True)

    def delete(self, obj: Task):
        keys = get_task_keys(obj.object_id, obj.content_type)
        with Lock(self.r, keys["lock_key"], expire=30):
            self.delete_redis_task(self.r, keys)
            obj.content_object.delete()

    def delete_qs(self, qs: QuerySet[Task]):
        for obj in qs:
            self.delete(obj)


class TaskDetail:
    template_name = "tasks/task/detail.html"
    model = Task

    def __init__(self, qs: QuerySet[Task]):
        self.qs = qs

    def get_object(self, pk: int):
        return self.qs.get(id=pk)

    def get(self, request: HttpRequest, pk: int, *args):
        obj = self.get_object(pk=pk)
        content_object = obj.content_object
        return render(
            request=request,
            template_name=self.template_name,
            context={"object": obj, "object_type": content_object},
        )

    @classmethod
    def get_queryset(cls, request: HttpRequest):
        queryset = (
            cls.model.objects.all()
            .filter(user=request.user)
            .prefetch_related("content_object")
        )
        return queryset
