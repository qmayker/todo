from logging import Logger
from abc import ABC, abstractmethod
from django.utils import timezone
from django.core.exceptions import ValidationError


class TimeValidation(ABC):
    def __init__(
        self, cd, changed_data: list[str], logger: Logger, FIELDS: dict[str, str]
    ):
        self.cd = cd
        self.changed_data = changed_data
        self.logger = logger
        self.end_name = FIELDS.get("end")
        self.start_name = FIELDS.get("start")
        self.start = self.cd.get(self.start_name)
        self.end = self.cd.get(self.end_name)
        self.now = timezone.now()
        if self.cd.get(self.start_name) is None:
            self.cd[self.start_name] = self.now

    def time_validation(self):
        if not self.changed_data:
            return
        if not self.start or not self.end:
            return
        if self.end <= self.start:
            raise ValidationError(
                {self.end_name: "End time cannot be earlier than start time"}
            )

    @abstractmethod
    def validate(self): ...
