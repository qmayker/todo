import logging
from django.utils import timezone
from django.core.exceptions import ValidationError
from tasks.models import Recurring, RecurringState
from .validation import TimeValidation


logger = logging.getLogger(__name__)


# TODO if only end_time changed - 
# TODO - task deleting.
class RecurringServices:
    def __init__(self, obj: Recurring, changed_data: list[str]):
        self.obj = obj
        self.changed_data = changed_data

    def create_recurring_state(self) -> RecurringState:
        if not self.changed_data:
            state = self.obj.state
            if state:
                return self.obj.state

        update_res = RecurringState.objects.update_or_create(
            recurring=self.obj,
            defaults={
                "next_time": self.obj.start_time,
                "ends_at": self.obj.start_time + self.obj.duration_time,
            },
        )
        state = update_res[0]
        return state


# TODO end_time causes error, with out changing time
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
