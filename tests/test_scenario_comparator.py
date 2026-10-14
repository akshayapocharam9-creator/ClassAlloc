import unittest
import copy
from typing import List, Dict

from models.scenario import ScenarioResult, ScenarioComparison, AllocationChange
from solver.result import SolverResult
from services.scenario_comparator import ScenarioComparator
from services.analytics import AnalyticsResult
from models import Allocation, Course, Classroom, TimeSlot, RoomType, DayOfWeek
from solver.scoring import ScoringConfig
import datetime

class TestScenarioComparator(unittest.TestCase):

    def setUp(self):
        # Create some dummy data using actual models
        self.c1 = Course("C1", "Course 1", "Prof A", 30, RoomType.LECTURE_HALL, set(), [])
        self.c2 = Course("C2", "Course 2", "Prof B", 20, RoomType.SEMINAR_ROOM, set(), [])
        
        self.cr1 = Classroom("CR1", "Room 1", "Bldg A", 40, RoomType.LECTURE_HALL, set(), [])
        self.cr2 = Classroom("CR2", "Room 2", "Bldg A", 30, RoomType.SEMINAR_ROOM, set(), [])
        self.cr3 = Classroom("CR3", "Room 3", "Bldg A", 50, RoomType.LECTURE_HALL, set(), [])
        
        start = datetime.time(9, 0)
        end = datetime.time(10, 0)
        self.ts1 = TimeSlot("TS1", DayOfWeek.MONDAY, start, end)
        self.ts2 = TimeSlot("TS2", DayOfWeek.TUESDAY, start, end)

        self.a1 = Allocation(self.c1, self.cr1, self.ts1, self.c1.faculty)
        self.a2 = Allocation(self.c2, self.cr2, self.ts2, self.c2.faculty)

        self.baseline_result = SolverResult(
            success=True,
            allocations=[self.a1, self.a2],
            score=80.0,
            score_breakdown={"capacity_efficiency": 70.0, "time_preference": 90.0}
        )

        self.scenario_result = ScenarioResult(
            success=True,
            solver_result=SolverResult(success=True),
            allocations=[self.a1, self.a2],
            score=80.0,
            score_breakdown={"capacity_efficiency": 70.0, "time_preference": 90.0}
        )
        
        self.baseline_analytics = AnalyticsResult(
            allocation_coverage_percentage=100.0,
            average_capacity_efficiency=70.0,
            total_teaching_hours=2.0,
            used_classrooms=2,
            unused_classrooms=1
        )
        
        self.scenario_analytics = AnalyticsResult(
            allocation_coverage_percentage=100.0,
            average_capacity_efficiency=70.0,
            total_teaching_hours=2.0,
            used_classrooms=2,
            unused_classrooms=1
        )
        self.scenario_result.analytics_result = self.scenario_analytics

    def test_identical_results_produce_zero_deltas(self):
        comp = ScenarioComparator.compare(self.baseline_result, self.scenario_result, self.baseline_analytics)
        self.assertEqual(comp.score_delta, 0.0)
        self.assertEqual(comp.score_direction, "UNCHANGED")
        self.assertEqual(comp.total_courses_affected, 0)
        self.assertEqual(comp.courses_classroom_changed, 0)
        self.assertEqual(comp.courses_time_slot_changed, 0)
        self.assertEqual(len(comp.allocation_changes), 0)
        for val in comp.breakdown_deltas.values():
            self.assertEqual(val, 0.0)

    def test_classroom_change_detected(self):
        a1_mod = Allocation(self.c1, self.cr3, self.ts1, self.c1.faculty) # changed cr1 to cr3
        self.scenario_result.allocations = [a1_mod, self.a2]
        
        comp = ScenarioComparator.compare(self.baseline_result, self.scenario_result)
        self.assertEqual(comp.total_courses_affected, 1)
        self.assertEqual(comp.courses_classroom_changed, 1)
        self.assertEqual(comp.courses_time_slot_changed, 0)
        self.assertEqual(comp.allocation_changes[0].course_id, "C1")
        self.assertEqual(comp.allocation_changes[0].baseline_classroom_id, "CR1")
        self.assertEqual(comp.allocation_changes[0].scenario_classroom_id, "CR3")

    def test_time_slot_change_detected(self):
        a2_mod = Allocation(self.c2, self.cr2, self.ts1, self.c2.faculty) # changed ts2 to ts1
        self.scenario_result.allocations = [self.a1, a2_mod]
        
        comp = ScenarioComparator.compare(self.baseline_result, self.scenario_result)
        self.assertEqual(comp.total_courses_affected, 1)
        self.assertEqual(comp.courses_classroom_changed, 0)
        self.assertEqual(comp.courses_time_slot_changed, 1)
        self.assertTrue(comp.allocation_changes[0].time_slot_changed)

    def test_both_changes_counted_once(self):
        a1_mod = Allocation(self.c1, self.cr3, self.ts2, self.c1.faculty) # both changed
        self.scenario_result.allocations = [a1_mod, self.a2]
        
        comp = ScenarioComparator.compare(self.baseline_result, self.scenario_result)
        self.assertEqual(comp.total_courses_affected, 1) # Counted once
        self.assertEqual(comp.courses_classroom_changed, 1)
        self.assertEqual(comp.courses_time_slot_changed, 1)
        self.assertTrue(comp.allocation_changes[0].classroom_changed)
        self.assertTrue(comp.allocation_changes[0].time_slot_changed)

    def test_score_delta_correct(self):
        self.scenario_result.score = 85.5
        comp = ScenarioComparator.compare(self.baseline_result, self.scenario_result)
        self.assertAlmostEqual(comp.score_delta, 5.5)
        self.assertEqual(comp.score_direction, "IMPROVED")

        self.scenario_result.score = 78.0
        comp2 = ScenarioComparator.compare(self.baseline_result, self.scenario_result)
        self.assertAlmostEqual(comp2.score_delta, -2.0)
        self.assertEqual(comp2.score_direction, "DECLINED")

    def test_score_breakdown_deltas(self):
        self.scenario_result.score_breakdown = {"capacity_efficiency": 80.0, "time_preference": 85.0}
        comp = ScenarioComparator.compare(self.baseline_result, self.scenario_result)
        self.assertAlmostEqual(comp.breakdown_deltas["capacity_efficiency"], 10.0)
        self.assertAlmostEqual(comp.breakdown_deltas["time_preference"], -5.0)

    def test_feasibility_changes_detected(self):
        self.scenario_result.success = False
        comp = ScenarioComparator.compare(self.baseline_result, self.scenario_result)
        self.assertTrue(comp.feasibility_changed)
        self.assertFalse(comp.scenario_feasible)

    def test_infeasible_does_not_crash(self):
        self.scenario_result.success = False
        self.scenario_result.allocations = []
        self.scenario_result.score = 0.0
        self.scenario_result.score_breakdown = {}
        comp = ScenarioComparator.compare(self.baseline_result, self.scenario_result)
        self.assertTrue(comp.feasibility_changed)
        self.assertEqual(len(comp.newly_unallocated_course_ids), 2) # Both became unallocated
        self.assertEqual(comp.total_courses_affected, 0) # Removed altogether, not moved

    def test_missing_or_new_courses(self):
        self.scenario_result.allocations = [self.a1] # c2 unallocated
        comp1 = ScenarioComparator.compare(self.baseline_result, self.scenario_result)
        self.assertIn("C2", comp1.newly_unallocated_course_ids)
        self.assertEqual(len(comp1.newly_allocated_course_ids), 0)

        # Baseline only has a1, scenario has a1 and a2
        self.baseline_result.allocations = [self.a1]
        self.scenario_result.allocations = [self.a1, self.a2]
        comp2 = ScenarioComparator.compare(self.baseline_result, self.scenario_result)
        self.assertIn("C2", comp2.newly_allocated_course_ids)
        self.assertEqual(len(comp2.newly_unallocated_course_ids), 0)

    def test_failure_information_preserved(self):
        self.scenario_result.success = False
        self.scenario_result.failure_reasons = {"C1": "Constraint unsatisfiable"}
        comp = ScenarioComparator.compare(self.baseline_result, self.scenario_result)
        self.assertEqual(comp.failure_reasons["C1"], "Constraint unsatisfiable")

    def test_analytics_deltas(self):
        self.scenario_analytics.allocation_coverage_percentage = 90.0
        self.scenario_analytics.used_classrooms = 1
        comp = ScenarioComparator.compare(self.baseline_result, self.scenario_result, self.baseline_analytics)
        self.assertAlmostEqual(comp.analytics_deltas["allocation_coverage_percentage"], -10.0)
        self.assertEqual(comp.analytics_deltas["used_classrooms"], -1)
        self.assertEqual(comp.analytics_deltas["unused_classrooms"], 0)

    def test_no_mutation(self):
        # Ensure comparator doesn't mutate inputs
        b_copy = copy.deepcopy(self.baseline_result)
        s_copy = copy.deepcopy(self.scenario_result)
        ScenarioComparator.compare(self.baseline_result, self.scenario_result, self.baseline_analytics)
        self.assertEqual(len(self.baseline_result.allocations), len(b_copy.allocations))
        self.assertEqual(len(self.scenario_result.allocations), len(s_copy.allocations))

if __name__ == '__main__':
    unittest.main()
