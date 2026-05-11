from django.db.models import QuerySet
from .task_statuses import Status

class CeleryTaskQueryset(QuerySet):

    def update_completed(self, celery_id: str):
        return self.filter(
            celery_id=celery_id, status=Status.RUNNING
        ).update(status=Status.COMPLETED)
    