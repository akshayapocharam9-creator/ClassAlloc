from models import Course, Classroom, TimeSlot, Allocation
from typing import Dict

def satisfies_static_constraints(course: Course, classroom: Classroom, time_slot: TimeSlot) -> bool:
    """
    Checks if a candidate classroom and time slot satisfy the course's strict static requirements.
    """
    if classroom.capacity < course.student_count:
        return False
        
    if classroom.room_type != course.required_room_type:
        return False
        
    if not course.required_features.issubset(classroom.features):
        return False
        
    if time_slot.id not in [ts.id for ts in course.preferred_time_slots]:
        return False
        
    if time_slot.id not in [ts.id for ts in classroom.available_time_slots]:
        return False
        
    return True

def satisfies_dynamic_constraints(
    course: Course, 
    classroom: Classroom, 
    time_slot: TimeSlot, 
    current_assignment: Dict[str, Allocation]
) -> bool:
    """
    Checks dynamic constraints against the current partial assignment.
    (Classroom conflicts and Faculty conflicts).
    """
    for _, allocation in current_assignment.items():
        # Classroom conflict: same classroom hosted at the same time slot
        if allocation.classroom.id == classroom.id and allocation.time_slot.id == time_slot.id:
            return False
            
        # Faculty conflict: same faculty member teaching at the same time slot
        if allocation.faculty == course.faculty and allocation.time_slot.id == time_slot.id:
            return False
            
    return True
