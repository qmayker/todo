from datetime import datetime
from typing import NamedTuple


class TaskSchedule(NamedTuple):
    eta: datetime | None
    schedule: bool
