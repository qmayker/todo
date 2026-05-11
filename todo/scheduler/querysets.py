from django.db.models import QuerySet
from .task_statuses import Status

class CeleryTaskQueryset(QuerySet):

    def update_completed(self, celery_id: str):
        return self.filter(
            celery_id=celery_id, status=Status.RUNNING
        ).update(status=Status.COMPLETED)
    
    def start_running(self, celery_id:str, status:Status):
        return self.filter(celery_id=celery_id, status=status).update(
            status=Status.RUNNING
        )
    
    def update_error(self, celery_id:str):
        return self.filter(
            celery_id=celery_id, status=Status.RUNNING
        ).update(status=Status.ERROR)
    