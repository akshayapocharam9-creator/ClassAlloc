import unittest
import datetime
from models import Course, Classroom, TimeSlot, Allocation, RoomType, Feature, DayOfWeek
from services.timetable import TimetableService

class TestTimetableService(unittest.TestCase):
    def setUp(self):
        self.ts1 = TimeSlot(id="ts1", day=DayOfWeek.MONDAY, start_time=datetime.time(9,0), end_time=datetime.time(10,0))
        self.ts2 = TimeSlot(id="ts2", day=DayOfWeek.TUESDAY, start_time=datetime.time(14,0), end_time=datetime.time(15,0))
        
        self.cr1 = Classroom(id="cr1", name="R1", building="B", capacity=100, room_type=RoomType.LECTURE_HALL, features=set(), available_time_slots=[self.ts1, self.ts2])
        self.cr2 = Classroom(id="cr2", name="R2", building="B", capacity=100, room_type=RoomType.LECTURE_HALL, features=set(), available_time_slots=[self.ts1, self.ts2])
        
        self.c1 = Course(id="c1", name="C1", faculty="F1", student_count=20, required_room_type=RoomType.LECTURE_HALL, required_features=set(), preferred_time_slots=[self.ts1], section="A")
        self.c2 = Course(id="c2", name="C2", faculty="F2", student_count=80, required_room_type=RoomType.LECTURE_HALL, required_features=set(), preferred_time_slots=[self.ts2], section="B")
        
        self.allocations = [
            Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts1, faculty="F1"),
            Allocation(course=self.c2, classroom=self.cr2, time_slot=self.ts2, faculty="F2")
        ]

    def test_get_university_timetable_no_filters(self):
        entries = TimetableService.get_university_timetable(self.allocations)
        self.assertEqual(len(entries), 2)
        # Check ordering: Monday before Tuesday
        self.assertEqual(entries[0].course_name, "C1")
        self.assertEqual(entries[1].course_name, "C2")

    def test_get_university_timetable_filters(self):
        entries = TimetableService.get_university_timetable(self.allocations, day_filter="Tuesday")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].course_name, "C2")

        entries = TimetableService.get_university_timetable(self.allocations, faculty_filter="F1")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].course_name, "C1")

        entries = TimetableService.get_university_timetable(self.allocations, classroom_filter="R2")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].course_name, "C2")
        
        entries = TimetableService.get_university_timetable(self.allocations, section_filter="A")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].course_name, "C1")

    def test_get_room_timetable(self):
        entries = TimetableService.get_room_timetable(self.allocations, "R1")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].classroom_name, "R1")

    def test_get_faculty_timetable(self):
        entries = TimetableService.get_faculty_timetable(self.allocations, "F2")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].faculty, "F2")

    def test_get_section_timetable(self):
        entries = TimetableService.get_section_timetable(self.allocations, "B")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].section, "B")

    def test_getters(self):
        days = TimetableService.get_all_days(self.allocations)
        self.assertEqual(days, ["Monday", "Tuesday"])
        
        rooms = TimetableService.get_all_classrooms(self.allocations)
        self.assertEqual(rooms, ["R1", "R2"])
        
        fac = TimetableService.get_all_faculty(self.allocations)
        self.assertEqual(fac, ["F1", "F2"])
        
        sections = TimetableService.get_all_sections(self.allocations)
        self.assertEqual(sections, ["A", "B"])

if __name__ == '__main__':
    unittest.main()
