import unittest
import datetime
from models import Course, Classroom, TimeSlot, Allocation, RoomType, Feature, DayOfWeek
from solver.scoring import Scoring
from services.schedule_explanation import ScheduleExplainer

class TestExplainability(unittest.TestCase):
    def setUp(self):
        self.ts1 = TimeSlot(id="ts1", day=DayOfWeek.MONDAY, start_time=datetime.time(9,0), end_time=datetime.time(10,0))
        self.ts2 = TimeSlot(id="ts2", day=DayOfWeek.MONDAY, start_time=datetime.time(14,0), end_time=datetime.time(15,0))
        
        self.cr = Classroom(id="cr1", name="R1", building="B", capacity=100, room_type=RoomType.LECTURE_HALL, features={Feature.PROJECTOR}, available_time_slots=[self.ts1, self.ts2])
        
        self.c1 = Course(id="c1", name="C1", faculty="F1", student_count=20, required_room_type=RoomType.LECTURE_HALL, required_features=set(), preferred_time_slots=[self.ts1, self.ts2], section=None)
        self.c2 = Course(id="c2", name="C2", faculty="F1", student_count=80, required_room_type=RoomType.LECTURE_HALL, required_features={Feature.PROJECTOR}, preferred_time_slots=[self.ts2], section=None)
        
        self.allocs = [
            Allocation(course=self.c1, classroom=self.cr, time_slot=self.ts1, faculty="F1"),
            Allocation(course=self.c2, classroom=self.cr, time_slot=self.ts2, faculty="F1")
        ]

    def test_aggregate_score_unchanged(self):
        # We did not change Scoring.evaluate
        score, breakdown = Scoring.evaluate(self.allocs)
        self.assertIn("capacity_efficiency", breakdown)
        self.assertTrue(score > 0)

    def test_capacity_explanation(self):
        expl = ScheduleExplainer.explain(self.allocs)
        # c1 cap eff: 20/100 = 20%
        # c2 cap eff: 80/100 = 80%
        a1 = next(a for a in expl.allocations if a.course_id == "c1")
        a2 = next(a for a in expl.allocations if a.course_id == "c2")
        self.assertAlmostEqual(a1.cap_eff, 20.0)
        self.assertAlmostEqual(a2.cap_eff, 80.0)
        
        # Test lowest efficiency correctly identified
        cap_losses = [a for a in expl.allocations if a.cap_eff < 100.0]
        cap_losses.sort(key=lambda x: x.cap_eff)
        self.assertEqual(cap_losses[0].course_id, "c1")

    def test_time_preference_explanation(self):
        expl = ScheduleExplainer.explain(self.allocs)
        a1 = next(a for a in expl.allocations if a.course_id == "c1")
        # c1 got ts1, which is index 0 -> score 100
        self.assertEqual(a1.time_pref_score, 100.0)
        self.assertIn("#1", a1.time_pref_details)
        
        # c2 got ts2, which is index 0 -> score 100
        a2 = next(a for a in expl.allocations if a.course_id == "c2")
        self.assertEqual(a2.time_pref_score, 100.0)

    def test_feature_explanation(self):
        expl = ScheduleExplainer.explain(self.allocs)
        a1 = next(a for a in expl.allocations if a.course_id == "c1")
        # c1 requires 0, cr has 1. Feature score should be 50.0
        self.assertEqual(a1.feat_eff, 50.0)
        
        a2 = next(a for a in expl.allocations if a.course_id == "c2")
        # c2 requires 1, cr has 1. Feature score should be 100.0
        self.assertEqual(a2.feat_eff, 100.0)

    def test_timetable_explanation(self):
        expl = ScheduleExplainer.explain(self.allocs)
        tq = expl.timetable_qualities[0]
        # F1 Monday has 9:00 and 14:00 (5 hour gap) -> >2 hours -> 1 gap
        self.assertEqual(tq.gaps, 1)
        self.assertEqual(tq.score, 70.0)

    def test_explanation_consistent_with_aggregate(self):
        score, breakdown = Scoring.evaluate(self.allocs)
        expl = ScheduleExplainer.explain(self.allocs)
        
        # Manual average
        avg_cap = sum(a.cap_eff for a in expl.allocations) / len(expl.allocations)
        self.assertAlmostEqual(breakdown["capacity_efficiency"], avg_cap)
        
        avg_time = sum(a.time_pref_score for a in expl.allocations) / len(expl.allocations)
        self.assertAlmostEqual(breakdown["time_preference"], avg_time)
        
        avg_feat = sum(a.feat_eff for a in expl.allocations) / len(expl.allocations)
        self.assertAlmostEqual(breakdown["feature_efficiency"], avg_feat)

if __name__ == "__main__":
    unittest.main()
