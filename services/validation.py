from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from models import Allocation, Course, TimeSlot, Classroom

@dataclass
class ConstraintViolation:
    rule_name: str
    severity: str
    explanation: str
    involved_allocations: List[Allocation] = field(default_factory=list)
    details: str = ""

@dataclass
class ValidationResult:
    valid: bool
    violations: List[ConstraintViolation] = field(default_factory=list)
    passed_rules: List[str] = field(default_factory=list)
    total_allocations: int = 0

class ValidationService:
    @staticmethod
    def validate_allocations(allocations: List[Allocation], all_courses: List[Course], all_time_slots: List[TimeSlot]) -> ValidationResult:
        result = ValidationResult(valid=True, total_allocations=len(allocations))
        violations = []
        passed_rules = set([
            "Classroom double-booking",
            "Faculty double-booking",
            "Capacity bounds respected",
            "Room Type matched",
            "Required Features present",
            "Time Slots valid",
            "Course Assignment unique",
            "All courses allocated"
        ])

        cr_ts_map = {}
        fac_ts_map = {}
        allocated_course_ids = set()
        duplicate_courses = set()
        
        valid_ts_ids = {ts.id for ts in all_time_slots}

        for a in allocations:
            # 1. Capacity
            if a.classroom.capacity < a.course.student_count:
                violations.append(ConstraintViolation(
                    rule_name="Capacity bounds respected",
                    severity="ERROR",
                    explanation=f"Course {a.course.name} has {a.course.student_count} students but assigned room {a.classroom.name} only holds {a.classroom.capacity}.",
                    involved_allocations=[a]
                ))
                passed_rules.discard("Capacity bounds respected")

            # 2. Room Type
            if a.classroom.room_type != a.course.required_room_type:
                violations.append(ConstraintViolation(
                    rule_name="Room Type matched",
                    severity="ERROR",
                    explanation=f"Course {a.course.name} requires {a.course.required_room_type.value}, but {a.classroom.name} is {a.classroom.room_type.value}.",
                    involved_allocations=[a]
                ))
                passed_rules.discard("Room Type matched")

            # 3. Features
            if not a.course.required_features.issubset(a.classroom.features):
                missing = a.course.required_features - a.classroom.features
                missing_str = ", ".join([f.value for f in missing])
                violations.append(ConstraintViolation(
                    rule_name="Required Features present",
                    severity="ERROR",
                    explanation=f"Room {a.classroom.name} is missing required features for {a.course.name}: {missing_str}.",
                    involved_allocations=[a]
                ))
                passed_rules.discard("Required Features present")

            # 4. Time Slot Validity
            if a.time_slot.id not in valid_ts_ids:
                violations.append(ConstraintViolation(
                    rule_name="Time Slots valid",
                    severity="ERROR",
                    explanation=f"Allocation for {a.course.name} uses an invalid or non-existent time slot ID: {a.time_slot.id}.",
                    involved_allocations=[a]
                ))
                passed_rules.discard("Time Slots valid")

            # 5. Course Uniqueness
            if a.course.id in allocated_course_ids:
                duplicate_courses.add(a.course.id)
                passed_rules.discard("Course Assignment unique")
            allocated_course_ids.add(a.course.id)

            # Maps for double booking
            cr_ts = (a.classroom.id, a.time_slot.id)
            if cr_ts not in cr_ts_map:
                cr_ts_map[cr_ts] = []
            cr_ts_map[cr_ts].append(a)

            fac_ts = (a.faculty, a.time_slot.id)
            if fac_ts not in fac_ts_map:
                fac_ts_map[fac_ts] = []
            fac_ts_map[fac_ts].append(a)

        # Process Classroom double-booking
        for cr_ts, allocs in cr_ts_map.items():
            if len(allocs) > 1:
                cr_name = allocs[0].classroom.name
                ts_str = f"{allocs[0].time_slot.day.value} {allocs[0].time_slot.start_time.strftime('%H:%M')}"
                course_names = ", ".join([a.course.name for a in allocs])
                violations.append(ConstraintViolation(
                    rule_name="Classroom double-booking",
                    severity="ERROR",
                    explanation=f"Room {cr_name} is double-booked at {ts_str} by: {course_names}.",
                    involved_allocations=allocs
                ))
                passed_rules.discard("Classroom double-booking")

        # Process Faculty double-booking
        for fac_ts, allocs in fac_ts_map.items():
            if len(allocs) > 1:
                fac = allocs[0].faculty
                ts_str = f"{allocs[0].time_slot.day.value} {allocs[0].time_slot.start_time.strftime('%H:%M')}"
                course_names = ", ".join([a.course.name for a in allocs])
                violations.append(ConstraintViolation(
                    rule_name="Faculty double-booking",
                    severity="ERROR",
                    explanation=f"Faculty {fac} is double-booked at {ts_str} for: {course_names}.",
                    involved_allocations=allocs
                ))
                passed_rules.discard("Faculty double-booking")

        # Process Duplicate Allocations
        if duplicate_courses:
            for cid in duplicate_courses:
                dup_allocs = [a for a in allocations if a.course.id == cid]
                cname = dup_allocs[0].course.name
                violations.append(ConstraintViolation(
                    rule_name="Course Assignment unique",
                    severity="ERROR",
                    explanation=f"Course {cname} has been assigned {len(dup_allocs)} times.",
                    involved_allocations=dup_allocs
                ))

        # Missing courses
        all_c_ids = {c.id for c in all_courses}
        missing_courses = all_c_ids - allocated_course_ids
        if missing_courses:
            passed_rules.discard("All courses allocated")
            missing_names = ", ".join([c.name for c in all_courses if c.id in missing_courses])
            violations.append(ConstraintViolation(
                rule_name="All courses allocated",
                severity="WARNING", # Might just be unallocated dynamically
                explanation=f"The following courses are not allocated: {missing_names}.",
                involved_allocations=[]
            ))

        result.violations = violations
        result.passed_rules = list(passed_rules)
        result.valid = len([v for v in violations if v.severity == "ERROR"]) == 0
        return result
