import unittest
from datetime import time
from models import DayOfWeek, RoomType, Feature, TimeSlot, Classroom, Course
from solver.constraints import satisfies_static_constraints, satisfies_dynamic_constraints
from solver.csp_solver import CSPSolver
from services.data_loader import DataLoader

class TestCSPSolver(unittest.TestCase):
    def setUp(self):
        self.ts1 = TimeSlot("TS1", DayOfWeek.MONDAY, time(9, 0), time(10, 0))
        self.ts2 = TimeSlot("TS2", DayOfWeek.MONDAY, time(10, 0), time(11, 0))
        self.cr1 = Classroom("CR1", "Room 1", "B1", 30, RoomType.LECTURE_HALL, {Feature.PROJECTOR}, [self.ts1, self.ts2])
        self.cr2 = Classroom("CR2", "Room 2", "B1", 20, RoomType.SEMINAR_ROOM, {Feature.WHITEBOARD}, [self.ts1])
        
    def test_capacity_constraint(self):
        c = Course("C1", "Math", "Dr. A", 40, RoomType.LECTURE_HALL, {Feature.PROJECTOR}, [self.ts1])
        self.assertFalse(satisfies_static_constraints(c, self.cr1, self.ts1))
        
    def test_room_type_constraint(self):
        c = Course("C1", "Math", "Dr. A", 20, RoomType.SEMINAR_ROOM, set(), [self.ts1])
        self.assertFalse(satisfies_static_constraints(c, self.cr1, self.ts1))
        
    def test_feature_constraint(self):
        c = Course("C1", "Math", "Dr. A", 20, RoomType.LECTURE_HALL, {Feature.COMPUTERS}, [self.ts1])
        self.assertFalse(satisfies_static_constraints(c, self.cr1, self.ts1))
        
    def test_time_preference_constraint(self):
        c = Course("C1", "Math", "Dr. A", 20, RoomType.LECTURE_HALL, set(), [self.ts2])
        self.assertFalse(satisfies_static_constraints(c, self.cr1, self.ts1))
        self.assertTrue(satisfies_static_constraints(c, self.cr1, self.ts2))
        
    def test_classroom_conflict(self):
        from models import Allocation
        c1 = Course("C1", "Math", "Dr. A", 20, RoomType.LECTURE_HALL, set(), [self.ts1])
        c2 = Course("C2", "Phys", "Dr. B", 20, RoomType.LECTURE_HALL, set(), [self.ts1])
        
        assignment = {
            "C1": Allocation(c1, self.cr1, self.ts1, "Dr. A")
        }
        self.assertFalse(satisfies_dynamic_constraints(c2, self.cr1, self.ts1, assignment))
        self.assertTrue(satisfies_dynamic_constraints(c2, self.cr1, self.ts2, assignment))
        
    def test_faculty_conflict(self):
        from models import Allocation
        c1 = Course("C1", "Math", "Dr. A", 20, RoomType.LECTURE_HALL, set(), [self.ts1])
        c2 = Course("C2", "Phys", "Dr. A", 20, RoomType.SEMINAR_ROOM, set(), [self.ts1])
        
        assignment = {
            "C1": Allocation(c1, self.cr1, self.ts1, "Dr. A")
        }
        self.assertFalse(satisfies_dynamic_constraints(c2, self.cr2, self.ts1, assignment))

    def test_impossible_scenario(self):
        c1 = Course("C1", "Math", "Dr. A", 40, RoomType.LECTURE_HALL, set(), [self.ts1])
        solver = CSPSolver([self.cr1], [c1], [self.ts1])
        result = solver.solve()
        self.assertFalse(result.success)
        self.assertEqual(len(result.allocations), 0)
        self.assertIn("C1", result.failure_reasons)
        
    def test_full_dataset_solvable_and_optimized(self):
        loader = DataLoader("data")
        ts, cr, c = loader.load_all()
        solver = CSPSolver(cr, c, ts, max_solutions=10) # small limit for fast test
        result = solver.solve()
        self.assertTrue(result.success, f"Dataset should be solvable. Failures: {result.failure_reasons}")
        self.assertEqual(result.allocated_count, len(c))
        
        self.assertGreater(result.score, 0)
        self.assertGreaterEqual(result.stats.solutions_explored, 1)
        
        # Verify hard constraints in optimal output
        cr_ts_seen = set()
        fac_ts_seen = set()
        for alloc in result.allocations:
            self.assertGreaterEqual(alloc.classroom.capacity, alloc.course.student_count)
            self.assertEqual(alloc.classroom.room_type, alloc.course.required_room_type)
            self.assertTrue(alloc.course.required_features.issubset(alloc.classroom.features))
            cr_ts = (alloc.classroom.id, alloc.time_slot.id)
            fac_ts = (alloc.faculty, alloc.time_slot.id)
            self.assertNotIn(cr_ts, cr_ts_seen, "Classroom conflict found in solution")
            self.assertNotIn(fac_ts, fac_ts_seen, "Faculty conflict found in solution")
            cr_ts_seen.add(cr_ts)
            fac_ts_seen.add(fac_ts)

if __name__ == '__main__':
    unittest.main()
