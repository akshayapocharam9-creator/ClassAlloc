from dataclasses import dataclass
from datetime import time
from .enums import DayOfWeek

@dataclass(frozen=True)
class TimeSlot:
    id: str
    day: DayOfWeek
    start_time: time
    end_time: time

    def __post_init__(self):
        if self.start_time >= self.end_time:
            raise ValueError(f"start_time ({self.start_time}) must be before end_time ({self.end_time})")
