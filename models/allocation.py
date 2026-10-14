from dataclasses import dataclass
from .course import Course
from .classroom import Classroom
from .time_slot import TimeSlot

@dataclass
class Allocation:
    course: Course
    classroom: Classroom
    time_slot: TimeSlot
    faculty: str
    status: str = "Allocated"

    def __post_init__(self):
        if self.course.student_count > self.classroom.capacity:
            raise ValueError(
                f"Classroom capacity ({self.classroom.capacity}) is smaller than "
                f"course student count ({self.course.student_count})"
            )
        if self.course.required_room_type != self.classroom.room_type:
            raise ValueError(
                f"Classroom type ({self.classroom.room_type}) does not match "
                f"required room type ({self.course.required_room_type})"
            )
        if not self.course.required_features.issubset(self.classroom.features):
            missing = self.course.required_features - self.classroom.features
            raise ValueError(f"Classroom is missing required features: {missing}")
