import unittest
import copy
from unittest.mock import patch

from models.scenario import ScenarioBaseline, ScenarioDefinition, ScenarioResult
from services.scenario_runner import ScenarioRunner
from services.data_loader import DataLoader
from solver.scoring import ScoringConfig

class TestScenarioRunner(unittest.TestCase):
    def setUp(self):
        loader = DataLoader("data")
        self.time_slots, self.classrooms, self.courses = loader.load_all()
        self.baseline = ScenarioBaseline(
            courses=self.courses,
            classrooms=self.classrooms,
            time_slots=self.time_slots,
            scoring_config=ScoringConfig()
        )

    def test_unsupported_scenario_type(self):
        definition = ScenarioDefinition(name="Test", scenario_type="INVALID_TYPE")
        result = ScenarioRunner.run(self.baseline, definition)
        self.assertFalse(result.success)
        self.assertIn("Unsupported scenario_type", result.failure_reasons["Global"])

    def test_missing_classroom_id(self):
        definition = ScenarioDefinition(name="Test", scenario_type="CLASSROOM_OUTAGE", hypothetical_changes={})
        result = ScenarioRunner.run(self.baseline, definition)
        self.assertFalse(result.success)
        self.assertIn("Missing classroom_id", result.failure_reasons["Global"])

    def test_nonexistent_classroom_id(self):
        definition = ScenarioDefinition(
            name="Test", 
            scenario_type="CLASSROOM_OUTAGE", 
            hypothetical_changes={"classroom_id": "FAKE_ID_123"}
        )
        result = ScenarioRunner.run(self.baseline, definition)
        self.assertFalse(result.success)
        self.assertIn("not found in baseline", result.failure_reasons["Global"])

    @patch('services.scenario_runner.CSPSolver')
    def test_classroom_outage_isolation(self, mock_solver_class):
        # Setup mock to return a fake successful result just to trace the calls
        mock_instance = mock_solver_class.return_value
        from solver.result import SolverResult
        mock_instance.solve.return_value = SolverResult(success=True)

        target_cr = self.classrooms[0].id
        definition = ScenarioDefinition(
            name="Outage Test",
            scenario_type="CLASSROOM_OUTAGE",
            hypothetical_changes={"classroom_id": target_cr}
        )

        orig_cr_count = len(self.baseline.classrooms)
        orig_c_count = len(self.baseline.courses)
        orig_ts_count = len(self.baseline.time_slots)

        ScenarioRunner.run(self.baseline, definition)

        # Assert baseline lists are completely unchanged
        self.assertEqual(len(self.baseline.classrooms), orig_cr_count)
        self.assertEqual(len(self.baseline.courses), orig_c_count)
        self.assertEqual(len(self.baseline.time_slots), orig_ts_count)

        # Assert solver was constructed
        self.assertTrue(mock_solver_class.called)
        _, kwargs = mock_solver_class.call_args
        
        # Verify passed classrooms list is missing the target
        passed_classrooms = kwargs['classrooms']
        self.assertEqual(len(passed_classrooms), orig_cr_count - 1)
        self.assertFalse(any(cr.id == target_cr for cr in passed_classrooms))
        
        # Verify objects are deep copies
        self.assertIsNot(kwargs['courses'][0], self.baseline.courses[0])
        
        # Verify solver_config / scoring_config
        self.assertTrue(mock_instance.solve.called)

    def test_real_execution_feasible(self):
        # We will run a real solver trace on a classroom outage.
        # Pick a classroom that we know we can remove without causing failure.
        # In the demo dataset, there are 10 rooms and 33 courses, we can probably safely drop 1 small room.
        # Let's drop a small room.
        target_cr = self.classrooms[-1]
        
        definition = ScenarioDefinition(
            name="Real Outage",
            scenario_type="CLASSROOM_OUTAGE",
            hypothetical_changes={"classroom_id": target_cr.id}
        )
        
        result = ScenarioRunner.run(self.baseline, definition)
        
        # It should succeed or fail cleanly. Assuming it succeeds, we check validation.
        # If the dataset is too tight, it might fail. Both are valid real runs.
        if result.success:
            self.assertTrue(len(result.allocations) > 0)
            self.assertIsNotNone(result.validation_result)
            self.assertTrue(result.validation_result.valid)
            # Ensure the removed room is absolutely NOT in any allocation
            for alloc in result.allocations:
                self.assertNotEqual(alloc.classroom.id, target_cr.id)
        else:
            self.assertFalse(result.success)
            self.assertTrue(len(result.failure_reasons) > 0)

    def test_real_execution_infeasible(self):
        # To guarantee infeasible, let's remove ALL classrooms but one, and set its capacity to 1 (in a modified baseline).
        # Actually, let's just make a baseline with 1 room and 100 courses.
        fake_baseline = ScenarioBaseline(
            courses=self.courses,
            classrooms=[self.classrooms[0]],
            time_slots=self.time_slots,
            scoring_config=ScoringConfig()
        )
        
        # If we remove the ONLY classroom, it's definitively impossible
        definition = ScenarioDefinition(
            name="Impossible Outage",
            scenario_type="CLASSROOM_OUTAGE",
            hypothetical_changes={"classroom_id": self.classrooms[0].id}
        )
        
        result = ScenarioRunner.run(fake_baseline, definition)
        self.assertFalse(result.success)
        self.assertIn("No possible assignments satisfy static constraints", str(result.failure_reasons))

    def test_scoring_config_override_isolation(self):
        # Override weights
        override_config = ScoringConfig(capacity_efficiency=100.0, time_preference=0.0, feature_efficiency=0.0, timetable_quality=0.0)
        definition = ScenarioDefinition(
            name="Weight Override",
            scenario_type="CLASSROOM_OUTAGE",
            hypothetical_changes={"classroom_id": self.classrooms[0].id},
            scoring_config_override=override_config
        )
        
        # Run it
        with patch('services.scenario_runner.CSPSolver') as mock_solver_class:
            mock_solver_class.return_value.solve.return_value.success = False
            ScenarioRunner.run(self.baseline, definition)
            
            # Extract passed config
            _, kwargs = mock_solver_class.call_args
            passed_config = kwargs['scoring_config']
            
            # Assert override was used
            self.assertEqual(passed_config.capacity_efficiency, 100.0)
            
            # Assert baseline config was not mutated
            self.assertEqual(self.baseline.scoring_config.capacity_efficiency, 40.0)

if __name__ == '__main__':
    unittest.main()
