from dataclasses import dataclass, field
from typing import Set, List
from .enums import RoomType, Feature
from .time_slot import TimeSlot

@dataclass
class Classroom:
    id: str
    name: str
    building: str
    capacity: int
    room_type: RoomType
    features: Set[Feature] = field(default_factory=set)
    available_time_slots: List[TimeSlot] = field(default_factory=list)

    def __post_init__(self):
        if self.capacity <= 0:
            raise ValueError(f"Classroom capacity must be positive, got {self.capacity}")
