from django.db.models import QuerySet


class OneTimeQuerySet(QuerySet):
    def active(self):
        return self.filter(started=True, expired=False)

    def expired(self):
        return self.filter(expired=True, completed=False)


class HistoryQuerySet(QuerySet):
    def expired(self):
        return self.filter(completed=False)
    
    def get_detail_qs(self, user):
        return self.filter(task__user=user)


class TaskQuerySet(QuerySet):
    def get_detail_qs(self, user):
        return self.filter(user=user).prefetch_related("content_object")
