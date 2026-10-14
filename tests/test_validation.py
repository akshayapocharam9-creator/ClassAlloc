import unittest
import datetime
from models import Course, Classroom, TimeSlot, Allocation, RoomType, Feature, DayOfWeek
from services.validation import ValidationService

class TestValidationService(unittest.TestCase):
    def setUp(self):
        self.ts1 = TimeSlot(id="ts1", day=DayOfWeek.MONDAY, start_time=datetime.time(9,0), end_time=datetime.time(10,0))
        self.ts2 = TimeSlot(id="ts2", day=DayOfWeek.MONDAY, start_time=datetime.time(10,0), end_time=datetime.time(11,0))
        self.ts_invalid = TimeSlot(id="ts_invalid", day=DayOfWeek.SUNDAY, start_time=datetime.time(0,0), end_time=datetime.time(1,0))
        
        self.all_time_slots = [self.ts1, self.ts2]

        self.cr1 = Classroom(id="cr1", name="Room1", building="B", capacity=50, room_type=RoomType.LECTURE_HALL, features={Feature.PROJECTOR}, available_time_slots=[self.ts1, self.ts2])
        self.cr2 = Classroom(id="cr2", name="Room2", building="B", capacity=100, room_type=RoomType.SEMINAR_ROOM, features=set(), available_time_slots=[self.ts1, self.ts2])

        self.c1 = Course(id="c1", name="Course1", faculty="Dr. Smith", student_count=30, required_room_type=RoomType.LECTURE_HALL, required_features={Feature.PROJECTOR}, preferred_time_slots=[self.ts1])
        self.c2 = Course(id="c2", name="Course2", faculty="Dr. Jones", student_count=40, required_room_type=RoomType.SEMINAR_ROOM, required_features=set(), preferred_time_slots=[self.ts2])
        self.c3 = Course(id="c3", name="Course3", faculty="Dr. Smith", student_count=60, required_room_type=RoomType.LECTURE_HALL, required_features=set(), preferred_time_slots=[self.ts2])
        
        self.all_courses = [self.c1, self.c2]

    def test_valid_schedule(self):
        allocs = [
            Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts1, faculty=self.c1.faculty),
            Allocation(course=self.c2, classroom=self.cr2, time_slot=self.ts2, faculty=self.c2.faculty)
        ]
        result = ValidationService.validate_allocations(allocs, self.all_courses, self.all_time_slots)
        self.assertTrue(result.valid)
        self.assertEqual(len(result.violations), 0)

    def test_capacity_violation(self):
        a = Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts1, faculty=self.c1.faculty)
        # Mutate to make it invalid
        a.course.student_count = 200 # cr1 capacity is 50
        result = ValidationService.validate_allocations([a], [self.c1], self.all_time_slots)
        self.assertFalse(result.valid)
        vio = next(v for v in result.violations if v.rule_name == "Capacity bounds respected")
        self.assertEqual(len(vio.involved_allocations), 1)

    def test_missing_room_feature(self):
        a = Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts1, faculty=self.c1.faculty)
        # c1 requires PROJECTOR. Remove from cr1
        a.classroom.features = set()
        result = ValidationService.validate_allocations([a], [self.c1], self.all_time_slots)
        self.assertFalse(result.valid)
        vio = next(v for v in result.violations if v.rule_name == "Required Features present")
        self.assertEqual(len(vio.involved_allocations), 1)

    def test_invalid_time_slot(self):
        allocs = [
            Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts_invalid, faculty=self.c1.faculty)
        ]
        result = ValidationService.validate_allocations(allocs, [self.c1], self.all_time_slots)
        self.assertFalse(result.valid)
        vio = next(v for v in result.violations if v.rule_name == "Time Slots valid")
        self.assertEqual(len(vio.involved_allocations), 1)

    def test_duplicate_course_allocation(self):
        a1 = Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts1, faculty=self.c1.faculty)
        a2 = Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts2, faculty=self.c1.faculty) 
        allocs = [a1, a2]
        result = ValidationService.validate_allocations(allocs, [self.c1], self.all_time_slots)
        self.assertFalse(result.valid)
        vio = next(v for v in result.violations if v.rule_name == "Course Assignment unique")
        self.assertEqual(len(vio.involved_allocations), 2)

    def test_missing_course_allocation(self):
        allocs = [
            Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts1, faculty=self.c1.faculty)
        ]
        result = ValidationService.validate_allocations(allocs, self.all_courses, self.all_time_slots)
        vio = next(v for v in result.violations if v.rule_name == "All courses allocated")
        self.assertEqual(vio.severity, "WARNING")
        
    def test_multiple_violations_coexist(self):
        a = Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts_invalid, faculty=self.c1.faculty)
        a.course.student_count = 200 # capacity violation
        result = ValidationService.validate_allocations([a], [self.c1], self.all_time_slots)
        self.assertFalse(result.valid)
        rule_names = [v.rule_name for v in result.violations]
        self.assertIn("Capacity bounds respected", rule_names)
        self.assertIn("Time Slots valid", rule_names)

    def test_validation_does_not_mutate(self):
        allocs = [
            Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts1, faculty=self.c1.faculty)
        ]
        orig_len = len(allocs)
        ValidationService.validate_allocations(allocs, self.all_courses, self.all_time_slots)
        self.assertEqual(len(allocs), orig_len)
        self.assertEqual(allocs[0].classroom.id, "cr1")

    def test_classroom_double_booking(self):
        a1 = Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts1, faculty=self.c1.faculty)
        # c3 student count is 60, cr1 capacity is 50. Let's fix that.
        self.c3.student_count = 40
        a2 = Allocation(course=self.c3, classroom=self.cr1, time_slot=self.ts1, faculty=self.c3.faculty)
        result = ValidationService.validate_allocations([a1, a2], self.all_courses, self.all_time_slots)
        self.assertFalse(result.valid)
        vio = next(v for v in result.violations if v.rule_name == "Classroom double-booking")
        self.assertEqual(len(vio.involved_allocations), 2)

    def test_faculty_double_booking(self):
        a1 = Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts1, faculty="Dr. Smith")
        a2 = Allocation(course=self.c2, classroom=self.cr2, time_slot=self.ts1, faculty="Dr. Smith")
        result = ValidationService.validate_allocations([a1, a2], self.all_courses, self.all_time_slots)
        self.assertFalse(result.valid)
        vio = next(v for v in result.violations if v.rule_name == "Faculty double-booking")
        self.assertEqual(len(vio.involved_allocations), 2)

if __name__ == '__main__':
    unittest.main()
