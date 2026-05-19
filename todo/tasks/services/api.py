from django.db.models import QuerySet
from tasks.models import OneTime, RecurringStateHistory, Task, Recurring


# TODO  - custom templates for history(new url with task_id/history_id)
class TaskList:
    def __init__(self):
        self.filters = {"active": self.get_active, "expired": self.get_expired}

    def get_active(self, qs: QuerySet[Task]) -> dict:
        onetime = OneTime.objects.filter(task__in=qs).active().prefetch_related("task")
        recurring = Recurring.objects.filter(task__in=qs, state__is_running=True)

        return {"recurring": recurring, "onetime": onetime}

    def get_expired(self, qs: QuerySet[Task]):
        onetime = OneTime.objects.filter(task__in=qs).expired().prefetch_related("task")
        history = (
            RecurringStateHistory.objects.filter(task__in=qs)
            .expired()
            .select_related("task")
        )
        return {"onetime": onetime, "history": history}
