from django.urls import reverse

class TaskTypeMixin:
    def get_task(self):
        return self.task.first()

    def get_absolute_url(self):
        return reverse("tasks:detail", kwargs={"pk": self.get_task().pk})

    @property
    def task_name(self):
        return self.get_task().name
