from django.core.exceptions import ValidationError
from tasks.models import Recurring, RecurringState
from .types import TaskSchedule
from .validation import TimeValidation
from .celery import CeleryService
from .recurring_state import RecurringStateServices


class RecurringServices(CeleryService):
    CONTENT_TYPE_ID = None

    def __init__(self, obj_id: int, *args, **kwargs):
        super().__init__(obj_id=obj_id, *args, **kwargs)
        obj = Recurring.objects.select_related().only("state__id").get(id=obj_id)
        self.state_service = RecurringStateServices(obj.state.id)

    @staticmethod
    def create_recurring_state(
        changed_data: list[str], obj: Recurring
    ) -> RecurringState:
        if not changed_data:
            try:
                state = obj.state
                return obj.state
            except RecurringState.DoesNotExist:
                state = None

        update_res = RecurringState.objects.update_or_create(
            recurring=obj,
            defaults={
                "next_time": obj.start_time,
                "ends_at": obj.start_time + obj.duration_time,
            },
        )
        state = update_res[0]
        return state

    @classmethod
    def get_by_id(cls, id: int):
        return cls(Recurring.objects.get(id=id))

    @staticmethod
    def get_model() -> Recurring:
        return Recurring

    def start(self) -> TaskSchedule:
        return self.state_service.start()

    def end(self) -> TaskSchedule:
        return self.state_service.end()


class RecurringValidation(TimeValidation):
    FIELDS = {"start": "start_time", "end": "end_time"}

    def __init__(self, cd, changed_data: list[str], logger):
        super().__init__(cd, changed_data, logger, self.FIELDS)

    def validate_time(self):
        if self.end_name and self.start_name not in self.changed_data:
            return
        self.time_validation()

    def validate_end_time(self):
        if self.end_name not in self.changed_data:
            return
        if self.end <= self.now:
            raise ValidationError({self.end_name: "Must be in future, not past"})

    def validate(self):
        self.validate_time()
        self.validate_end_time()
