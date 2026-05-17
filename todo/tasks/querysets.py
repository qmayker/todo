from django.db.models import QuerySet, Q


class TaskQuerySet(QuerySet):
    def active(self):
        return self.filter(
            Q(onetime__started=True, onetime__expired=False)
            | Q(recurring__state__is_running=True)
        )

    def expired(self):
        return self.filter(
            Q(onetime__expired=True, onetime__completed=False)
            | Q(recurring__state__history__completed=False)
        )
