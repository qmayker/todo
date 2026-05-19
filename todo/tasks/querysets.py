from django.db.models import QuerySet


class OneTimeQuerySet(QuerySet):
    def active(self):
        return self.filter(started=True, expired=False)
    
    def expired(self):
        return self.filter(expired=True, completed=False)


class HistoryQuerySet(QuerySet):
    def expired(self):
        return self.filter(completed=False)
