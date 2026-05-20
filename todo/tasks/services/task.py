from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from redis import Redis
from redis_lock import Lock
from logging import Logger
from tasks.models import Task
from todo.celery import app
from .views import BaseViewService
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


class TaskViewService(BaseViewService):
    template_name = "tasks/task/detail.html"
    model = Task

    def __init__(self, qs: QuerySet[Task], pk: int):
        super().__init__(qs=qs, pk=pk)
        self.qs: QuerySet[Task]

    def get(self, request: HttpRequest, *args):
        content_object = self.object.content_object
        return render(
            request=request,
            template_name=self.template_name,
            context={"object": self.object, "object_type": content_object},
        )
