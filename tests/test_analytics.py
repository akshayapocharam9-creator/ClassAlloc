import unittest
import datetime
from models import Course, Classroom, TimeSlot, Allocation, RoomType, Feature, DayOfWeek
from services.analytics import AnalyticsService

class TestAnalyticsService(unittest.TestCase):
    def setUp(self):
        self.ts1 = TimeSlot(id="ts1", day=DayOfWeek.MONDAY, start_time=datetime.time(9,0), end_time=datetime.time(10,30)) # 1.5 hours
        self.ts2 = TimeSlot(id="ts2", day=DayOfWeek.MONDAY, start_time=datetime.time(11,0), end_time=datetime.time(12,0)) # 1.0 hours
        self.all_time_slots = [self.ts1, self.ts2]

        self.cr1 = Classroom(id="cr1", name="Room1", building="B", capacity=50, room_type=RoomType.LECTURE_HALL, features=set(), available_time_slots=[self.ts1, self.ts2])
        self.cr2 = Classroom(id="cr2", name="Room2", building="B", capacity=100, room_type=RoomType.SEMINAR_ROOM, features=set(), available_time_slots=[])
        self.all_classrooms = [self.cr1, self.cr2]

        self.c1 = Course(id="c1", name="Course1", faculty="Dr. Smith", student_count=30, required_room_type=RoomType.LECTURE_HALL, required_features=set(), preferred_time_slots=[self.ts1])
        self.c2 = Course(id="c2", name="Course2", faculty="Dr. Jones", student_count=40, required_room_type=RoomType.LECTURE_HALL, required_features=set(), preferred_time_slots=[self.ts2])
        self.c3 = Course(id="c3", name="Course3", faculty="Dr. Smith", student_count=20, required_room_type=RoomType.LECTURE_HALL, required_features=set(), preferred_time_slots=[self.ts2])
        self.all_courses = [self.c1, self.c2, self.c3]

        self.allocs = [
            Allocation(course=self.c1, classroom=self.cr1, time_slot=self.ts1, faculty="Dr. Smith"),
            Allocation(course=self.c2, classroom=self.cr1, time_slot=self.ts2, faculty="Dr. Jones")
        ]

    def test_classroom_utilization(self):
        report = AnalyticsService.generate_report(self.allocs, self.all_courses, self.all_classrooms, self.all_time_slots)
        
        # cr1 has 2 sessions out of 2 available
        cr1_stats = next(cr for cr in report.classroom_analytics if cr.classroom_id == "cr1")
        self.assertEqual(cr1_stats.allocated_sessions, 2)
        self.assertEqual(cr1_stats.available_sessions, 2)
        self.assertEqual(cr1_stats.utilization_percentage, 100.0)
        
        # cr2 has 0 sessions out of 0 available
        cr2_stats = next(cr for cr in report.classroom_analytics if cr.classroom_id == "cr2")
        self.assertEqual(cr2_stats.allocated_sessions, 0)
        self.assertEqual(cr2_stats.available_sessions, 0)
        self.assertEqual(cr2_stats.utilization_percentage, 0.0)

    def test_wasted_capacity(self):
        report = AnalyticsService.generate_report(self.allocs, self.all_courses, self.all_classrooms, self.all_time_slots)
        cr1_stats = next(cr for cr in report.classroom_analytics if cr.classroom_id == "cr1")
        
        # c1 has 30 students in cr1 (50 cap) -> wasted 20
        # c2 has 40 students in cr1 (50 cap) -> wasted 10
        # total wasted = 30
        self.assertEqual(cr1_stats.wasted_capacity, 30)

    def test_faculty_teaching_hours(self):
        report = AnalyticsService.generate_report(self.allocs, self.all_courses, self.all_classrooms, self.all_time_slots)
        
        smith_stats = next(f for f in report.faculty_analytics if f.faculty == "Dr. Smith")
        # c1 is 1.5 hours
        self.assertEqual(smith_stats.session_count, 1)
        self.assertAlmostEqual(smith_stats.total_teaching_hours, 1.5)

        jones_stats = next(f for f in report.faculty_analytics if f.faculty == "Dr. Jones")
        # c2 is 1.0 hours
        self.assertEqual(jones_stats.session_count, 1)
        self.assertAlmostEqual(jones_stats.total_teaching_hours, 1.0)

    def test_course_distribution(self):
        report = AnalyticsService.generate_report(self.allocs, self.all_courses, self.all_classrooms, self.all_time_slots)
        self.assertEqual(report.total_courses, 3)
        self.assertEqual(report.allocated_courses, 2)
        self.assertEqual(report.unallocated_courses, 1)
        self.assertAlmostEqual(report.allocation_coverage_percentage, 66.666, places=2)

    def test_classroom_usage_counts(self):
        report = AnalyticsService.generate_report(self.allocs, self.all_courses, self.all_classrooms, self.all_time_slots)
        self.assertEqual(report.total_classrooms, 2)
        self.assertEqual(report.used_classrooms, 1)
        self.assertEqual(report.unused_classrooms, 1)
        
    def test_time_slot_grouping(self):
        report = AnalyticsService.generate_report(self.allocs, self.all_courses, self.all_classrooms, self.all_time_slots)
        ts1_stats = next(ts for ts in report.time_slot_analytics if ts.time_slot_id == "ts1")
        self.assertEqual(ts1_stats.allocated_sessions, 1)
        
    def test_day_wise_grouping(self):
        report = AnalyticsService.generate_report(self.allocs, self.all_courses, self.all_classrooms, self.all_time_slots)
        day_stats = next(d for d in report.day_analytics if d.day == DayOfWeek.MONDAY.value)
        self.assertEqual(day_stats.allocated_sessions, 2)
        self.assertAlmostEqual(day_stats.teaching_hours, 2.5)
        
    def test_empty_allocations(self):
        report = AnalyticsService.generate_report([], self.all_courses, self.all_classrooms, self.all_time_slots)
        self.assertEqual(report.total_allocations, 0)
        self.assertEqual(report.allocated_courses, 0)
        self.assertEqual(report.unallocated_courses, 3)
        self.assertEqual(report.allocation_coverage_percentage, 0.0)
        self.assertEqual(report.used_classrooms, 0)

    def test_capacity_efficiency(self):
        report = AnalyticsService.generate_report(self.allocs, self.all_courses, self.all_classrooms, self.all_time_slots)
        # c1 eff: 30 / 50 = 60%
        # c2 eff: 40 / 50 = 80%
        # avg = 70%
        self.assertAlmostEqual(report.average_capacity_efficiency, 70.0)

if __name__ == '__main__':
    unittest.main()
