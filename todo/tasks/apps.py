from django.apps import AppConfig
from django.core.signals import setting_changed


class TasksConfig(AppConfig):
    name = "tasks"

    def ready(self):
        from .signals import task_delete_hander

        setting_changed.connect(task_delete_hander)
        return super().ready()
