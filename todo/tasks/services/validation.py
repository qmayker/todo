from datetime import datetime
from django.core.exceptions import ValidationError


def time_validation(start: datetime, end: datetime, changed_data: dict):
    if not changed_data:
        return
    if not start or not end:
        return
    if end <= start:
        raise ValidationError(
            {"end_time": "End time cannot be earlier than start time"}
        )
