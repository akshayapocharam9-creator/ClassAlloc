from dataclasses import dataclass, field
from typing import Set, List, Optional
from .enums import RoomType, Feature
from .time_slot import TimeSlot

@dataclass
class Course:
    id: str
    name: str
    faculty: str
    student_count: int
    required_room_type: RoomType
    required_features: Set[Feature] = field(default_factory=set)
    preferred_time_slots: List[TimeSlot] = field(default_factory=list)
    section: Optional[str] = None

    def __post_init__(self):
        if self.student_count < 0:
            raise ValueError(f"Course student count must be non-negative, got {self.student_count}")
