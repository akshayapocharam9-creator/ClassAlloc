import unittest
from datetime import time
from models import DayOfWeek, RoomType, Feature, TimeSlot, Classroom, Course, Allocation
from solver.scoring import Scoring

class TestScoring(unittest.TestCase):
    def setUp(self):
        self.ts1 = TimeSlot("TS1", DayOfWeek.MONDAY, time(9, 0), time(10, 0))
        self.ts2 = TimeSlot("TS2", DayOfWeek.MONDAY, time(10, 0), time(11, 0))
        
        self.cr_large = Classroom("CR1", "Large", "B1", 100, RoomType.LECTURE_HALL, {Feature.PROJECTOR})
        self.cr_small = Classroom("CR2", "Small", "B1", 30, RoomType.LECTURE_HALL, {Feature.PROJECTOR})
        
        self.course = Course("C1", "Math", "Dr. A", 25, RoomType.LECTURE_HALL, set(), [self.ts1, self.ts2])

    def test_capacity_efficiency(self):
        alloc_large = Allocation(self.course, self.cr_large, self.ts1, "Dr. A")
        score_large, breakdown_large = Scoring.evaluate([alloc_large])
        
        alloc_small = Allocation(self.course, self.cr_small, self.ts1, "Dr. A")
        score_small, breakdown_small = Scoring.evaluate([alloc_small])
        
        self.assertGreater(breakdown_small["capacity_efficiency"], breakdown_large["capacity_efficiency"])
        self.assertGreater(score_small, score_large)

    def test_time_preference(self):
        alloc_1 = Allocation(self.course, self.cr_small, self.ts1, "Dr. A")
        _, b1 = Scoring.evaluate([alloc_1])
        
        alloc_2 = Allocation(self.course, self.cr_small, self.ts2, "Dr. A")
        _, b2 = Scoring.evaluate([alloc_2])
        
        self.assertGreater(b1["time_preference"], b2["time_preference"])

    def test_feature_efficiency(self):
        cr_feature_heavy = Classroom("CR3", "Lab", "B1", 30, RoomType.LECTURE_HALL, {Feature.PROJECTOR, Feature.COMPUTERS, Feature.SMART_BOARD})
        
        alloc_heavy = Allocation(self.course, cr_feature_heavy, self.ts1, "Dr. A")
        _, b_heavy = Scoring.evaluate([alloc_heavy])
        
        alloc_light = Allocation(self.course, self.cr_small, self.ts1, "Dr. A")
        _, b_light = Scoring.evaluate([alloc_light])
        
        self.assertGreaterEqual(b_light["feature_efficiency"], b_heavy["feature_efficiency"])

    def test_deterministic_scoring(self):
        alloc = Allocation(self.course, self.cr_small, self.ts1, "Dr. A")
        score1, _ = Scoring.evaluate([alloc])
        score2, _ = Scoring.evaluate([alloc])
        self.assertEqual(score1, score2)

if __name__ == '__main__':
    unittest.main()
