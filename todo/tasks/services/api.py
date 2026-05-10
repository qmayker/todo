from tasks.querysets import TaskQuerySet


class TaskList:
    def __init__(self):
        self.filters = {"active": self.get_active, "expired": self.get_expired}

    def get_active(self, qs: TaskQuerySet):
        return qs.active()

    def get_expired(self, qs: TaskQuerySet):
        return qs.expired()
