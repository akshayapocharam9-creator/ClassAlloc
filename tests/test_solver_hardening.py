import unittest
import copy
from solver.scoring import Scoring, ScoringConfig
from solver.csp_solver import CSPSolver, SolverConfig
from services.data_loader import DataLoader

class TestSolverArchitectureHardening(unittest.TestCase):
    def setUp(self):
        loader = DataLoader("data")
        self.time_slots, self.classrooms, self.courses = loader.load_all()

    def test_default_scoring_config(self):
        config = ScoringConfig()
        self.assertEqual(config.capacity_efficiency, 40.0)
        self.assertEqual(config.time_preference, 20.0)
        self.assertEqual(config.feature_efficiency, 20.0)
        self.assertEqual(config.timetable_quality, 20.0)
        
        # Test backward compatibility behavior with Scoring.WEIGHTS
        self.assertEqual(Scoring.WEIGHTS["capacity_efficiency"], 40.0)

    def test_existing_formulas_unchanged(self):
        eff = Scoring.calc_capacity_efficiency(50, 100)
        self.assertEqual(eff, 50.0)

    def test_default_solver_output_validity(self):
        solver = CSPSolver(self.classrooms, self.courses, self.time_slots)
        result = solver.solve()
        self.assertTrue(result.success)
        self.assertGreater(result.score, 0)

    def test_configurations_are_independent(self):
        config1 = ScoringConfig(capacity_efficiency=100.0)
        config2 = ScoringConfig(capacity_efficiency=0.0)
        self.assertEqual(config1.capacity_efficiency, 100.0)
        self.assertEqual(config2.capacity_efficiency, 0.0)

    def test_no_global_mutation_on_run(self):
        config1 = ScoringConfig(capacity_efficiency=100.0, time_preference=0.0, feature_efficiency=0.0, timetable_quality=0.0)
        solver = CSPSolver(self.classrooms, self.courses, self.time_slots, scoring_config=config1)
        solver.solve()
        
        # Ensure default ScoringConfig remains 40/20/20/20
        default_config = ScoringConfig()
        self.assertEqual(default_config.capacity_efficiency, 40.0)

    def test_domain_ordering_responds_to_weights(self):
        # We find a course with multiple valid options
        course = self.courses[0] # Try first course
        
        # With high capacity efficiency priority
        config_cap = ScoringConfig(capacity_efficiency=100.0, time_preference=0.0, feature_efficiency=0.0, timetable_quality=0.0)
        solver_cap = CSPSolver(self.classrooms, [course], self.time_slots, scoring_config=config_cap)
        domains_cap = solver_cap._build_initial_domains()
        top_cr_cap = domains_cap[course.id][0][0] # cr of first domain element
        
        # With high feature priority
        config_feat = ScoringConfig(capacity_efficiency=0.0, time_preference=0.0, feature_efficiency=100.0, timetable_quality=0.0)
        solver_feat = CSPSolver(self.classrooms, [course], self.time_slots, scoring_config=config_feat)
        domains_feat = solver_feat._build_initial_domains()
        top_cr_feat = domains_feat[course.id][0][0]
        
        # They might be the same room depending on the dataset, but we're testing that the logic evaluates the weighted sum properly.
        # Just ensure _domain_heuristic gives different scores for the two configs.
        score_cap = solver_cap._domain_heuristic(course, top_cr_cap, domains_cap[course.id][0][1])
        score_feat = solver_feat._domain_heuristic(course, top_cr_feat, domains_feat[course.id][0][1])
        self.assertNotEqual(score_cap, score_feat)

    def test_max_solutions_configurable(self):
        # Default behavior via kwarg
        solver1 = CSPSolver(self.classrooms, self.courses, self.time_slots, max_solutions=10)
        self.assertEqual(solver1.solver_config.max_solutions, 10)
        result1 = solver1.solve()
        
        # via config
        solver2 = CSPSolver(self.classrooms, self.courses, self.time_slots, solver_config=SolverConfig(max_solutions=20))
        self.assertEqual(solver2.solver_config.max_solutions, 20)
        result2 = solver2.solve()
        
        self.assertTrue(result1.stats.solutions_explored <= 10)
        self.assertTrue(result2.stats.solutions_explored <= 20)

    def test_no_input_mutation(self):
        c_copy = copy.deepcopy(self.courses)
        solver = CSPSolver(self.classrooms, self.courses, self.time_slots)
        solver.solve()
        self.assertEqual(len(self.courses), len(c_copy))
        for i in range(len(self.courses)):
            self.assertEqual(self.courses[i].student_count, c_copy[i].student_count)

if __name__ == '__main__':
    unittest.main()
