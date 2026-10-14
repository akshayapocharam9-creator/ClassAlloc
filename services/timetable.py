from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from models import Allocation

@dataclass
class TimetableEntry:
    allocation: Allocation
    day: str
    time_str: str
    course_name: str
    faculty: str
    classroom_name: str
    section: Optional[str]

class TimetableService:
    DAY_ORDER = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}

    @staticmethod
    def _create_entry(a: Allocation) -> TimetableEntry:
        return TimetableEntry(
            allocation=a,
            day=a.time_slot.day.value,
            time_str=f"{a.time_slot.start_time.strftime('%H:%M')} - {a.time_slot.end_time.strftime('%H:%M')}",
            course_name=a.course.name,
            faculty=a.faculty,
            classroom_name=a.classroom.name,
            section=a.course.section
        )

    @staticmethod
    def get_university_timetable(allocations: List[Allocation], 
                                 day_filter: Optional[str] = None,
                                 time_filter: Optional[str] = None,
                                 classroom_filter: Optional[str] = None,
                                 faculty_filter: Optional[str] = None,
                                 section_filter: Optional[str] = None) -> List[TimetableEntry]:
        entries = []
        for a in allocations:
            if day_filter and day_filter != "All" and a.time_slot.day.value != day_filter:
                continue
            time_str = f"{a.time_slot.start_time.strftime('%H:%M')} - {a.time_slot.end_time.strftime('%H:%M')}"
            if time_filter and time_filter != "All" and time_str != time_filter:
                continue
            if classroom_filter and classroom_filter != "All" and a.classroom.name != classroom_filter:
                continue
            if faculty_filter and faculty_filter != "All" and a.faculty != faculty_filter:
                continue
            if section_filter and section_filter != "All" and a.course.section != section_filter:
                continue
            entries.append(TimetableService._create_entry(a))
            
        return sorted(entries, key=lambda e: (
            TimetableService.DAY_ORDER.get(e.day, 99),
            e.allocation.time_slot.start_time,
            e.classroom_name,
            e.course_name
        ))

    @staticmethod
    def get_room_timetable(allocations: List[Allocation], room_name: str) -> List[TimetableEntry]:
        return TimetableService.get_university_timetable(allocations, classroom_filter=room_name)

    @staticmethod
    def get_faculty_timetable(allocations: List[Allocation], faculty: str) -> List[TimetableEntry]:
        return TimetableService.get_university_timetable(allocations, faculty_filter=faculty)

    @staticmethod
    def get_section_timetable(allocations: List[Allocation], section: str) -> List[TimetableEntry]:
        return TimetableService.get_university_timetable(allocations, section_filter=section)

    @staticmethod
    def get_all_days(allocations: List[Allocation]) -> List[str]:
        days = list(set(a.time_slot.day.value for a in allocations))
        return sorted(days, key=lambda d: TimetableService.DAY_ORDER.get(d, 99))

    @staticmethod
    def get_all_times(allocations: List[Allocation]) -> List[str]:
        times = list(set(f"{a.time_slot.start_time.strftime('%H:%M')} - {a.time_slot.end_time.strftime('%H:%M')}" for a in allocations))
        return sorted(times)

    @staticmethod
    def get_all_classrooms(allocations: List[Allocation]) -> List[str]:
        return sorted(list(set(a.classroom.name for a in allocations)))

    @staticmethod
    def get_all_faculty(allocations: List[Allocation]) -> List[str]:
        return sorted(list(set(a.faculty for a in allocations)))

    @staticmethod
    def get_all_sections(allocations: List[Allocation]) -> List[str]:
        sections = set(a.course.section for a in allocations if a.course.section is not None)
        return sorted(list(sections))

