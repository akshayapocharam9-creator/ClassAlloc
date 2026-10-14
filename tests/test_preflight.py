import unittest
from models import Course, Classroom, TimeSlot, RoomType, Feature, DayOfWeek
from services.preflight import PreflightIntelligence
import datetime

class TestPreflightIntelligence(unittest.TestCase):
    def setUp(self):
        self.ts = TimeSlot(id="ts1", day=DayOfWeek.MONDAY, start_time=datetime.time(9,0), end_time=datetime.time(10,0))
        self.cr1 = Classroom(id="cr1", name="R1", building="B", capacity=30, room_type=RoomType.LECTURE_HALL, features={Feature.PROJECTOR}, available_time_slots=[self.ts])
        
    def test_sufficient_capacity(self):
        c = Course(id="c1", name="C1", faculty="F1", student_count=20, required_room_type=RoomType.LECTURE_HALL, required_features={Feature.PROJECTOR}, preferred_time_slots=[self.ts], section=None)
        preflight = PreflightIntelligence([self.cr1], [c], [self.ts])
        report = preflight.analyze()
        self.assertEqual(report.critical_count, 1)
        self.assertEqual(report.overall_status, "CRITICAL") 
        
    def test_exceeding_capacity(self):
        c = Course(id="c1", name="C1", faculty="F1", student_count=50, required_room_type=RoomType.LECTURE_HALL, required_features={Feature.PROJECTOR}, preferred_time_slots=[self.ts], section=None)
        preflight = PreflightIntelligence([self.cr1], [c], [self.ts])
        report = preflight.analyze()
        self.assertTrue(any(f.category == "Capacity Feasibility" and f.severity == "CRITICAL" for f in report.findings))

    def test_room_type_unavailable(self):
        c = Course(id="c1", name="C1", faculty="F1", student_count=20, required_room_type=RoomType.COMPUTER_LAB, required_features=set(), preferred_time_slots=[self.ts], section=None)
        preflight = PreflightIntelligence([self.cr1], [c], [self.ts])
        report = preflight.analyze()
        self.assertTrue(any(f.category == "Room Compatibility" and f.severity == "CRITICAL" for f in report.findings))

    def test_feature_unavailable(self):
        c = Course(id="c1", name="C1", faculty="F1", student_count=20, required_room_type=RoomType.LECTURE_HALL, required_features={Feature.SMART_BOARD}, preferred_time_slots=[self.ts], section=None)
        preflight = PreflightIntelligence([self.cr1], [c], [self.ts])
        report = preflight.analyze()
        self.assertTrue(any(f.category == "Room Compatibility" and f.severity == "CRITICAL" for f in report.findings))

    def test_zero_scheduling_possibilities(self):
        ts2 = TimeSlot(id="ts2", day=DayOfWeek.TUESDAY, start_time=datetime.time(9,0), end_time=datetime.time(10,0))
        c = Course(id="c1", name="C1", faculty="F1", student_count=20, required_room_type=RoomType.LECTURE_HALL, required_features={Feature.PROJECTOR}, preferred_time_slots=[ts2], section=None)
        # the room cr1 only has ts1 available, so zero overlap
        preflight = PreflightIntelligence([self.cr1], [c], [self.ts, ts2])
        report = preflight.analyze()
        self.assertTrue(any(f.category == "Time-Slot Feasibility" and f.severity == "CRITICAL" for f in report.findings))

    def test_healthy_dataset(self):
        # Create a healthy dataset with domain size > 3
        ts_list = [
            TimeSlot(id=f"ts{i}", day=DayOfWeek.MONDAY, start_time=datetime.time(i,0), end_time=datetime.time(i+1,0))
            for i in range(9, 14) # 5 time slots
        ]
        cr = Classroom(id="cr1", name="R1", building="B", capacity=50, room_type=RoomType.LECTURE_HALL, features=set(), available_time_slots=ts_list)
        c = Course(id="c1", name="C1", faculty="F1", student_count=20, required_room_type=RoomType.LECTURE_HALL, required_features=set(), preferred_time_slots=ts_list, section=None)
        
        preflight = PreflightIntelligence([cr], [c], ts_list)
        report = preflight.analyze()
        
        # There should be no issues at all for the course
        self.assertEqual(report.critical_count, 0)
        self.assertEqual(report.warning_count, 0)
        self.assertEqual(report.overall_status, "HEALTHY")

    def test_small_domain_warning(self):
        ts_list = [
            TimeSlot(id=f"ts{i}", day=DayOfWeek.MONDAY, start_time=datetime.time(i,0), end_time=datetime.time(i+1,0))
            for i in range(9, 12) # 3 time slots
        ]
        cr = Classroom(id="cr1", name="R1", building="B", capacity=50, room_type=RoomType.LECTURE_HALL, features=set(), available_time_slots=ts_list)
        c = Course(id="c1", name="C1", faculty="F1", student_count=20, required_room_type=RoomType.LECTURE_HALL, required_features=set(), preferred_time_slots=ts_list, section=None)
        
        preflight = PreflightIntelligence([cr], [c], ts_list)
        report = preflight.analyze()
        
        # Domain size should be 3, which is a WARNING
        self.assertEqual(report.critical_count, 0)
        self.assertEqual(report.warning_count, 1)
        self.assertEqual(report.overall_status, "WARNING")
        self.assertTrue(any(f.category == "Domain Size" and f.severity == "WARNING" for f in report.findings))

if __name__ == "__main__":
    unittest.main()
