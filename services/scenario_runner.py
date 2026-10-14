import copy
from typing import List
from models.scenario import ScenarioBaseline, ScenarioDefinition, ScenarioResult
from models import Classroom
from solver.csp_solver import CSPSolver
from solver.scoring import ScoringConfig
from services.validation import ValidationService

class ScenarioRunner:
    @staticmethod
    def run(baseline: ScenarioBaseline, definition: ScenarioDefinition) -> ScenarioResult:
        # 1. Validate scenario_type
        if definition.scenario_type != "CLASSROOM_OUTAGE":
            return ScenarioResult(
                success=False,
                failure_reasons={"Global": f"Unsupported scenario_type: {definition.scenario_type}"}
            )

        # 2. Extract hypothetical changes
        classroom_id = definition.hypothetical_changes.get("classroom_id")
        if not classroom_id:
            return ScenarioResult(
                success=False,
                failure_reasons={"Global": "Missing classroom_id in hypothetical_changes"}
            )
            
        # Verify classroom exists in baseline
        if not any(cr.id == classroom_id for cr in baseline.classrooms):
            return ScenarioResult(
                success=False,
                failure_reasons={"Global": f"Classroom {classroom_id} not found in baseline"}
            )

        # 3. Deep-copy baseline inputs to ensure strict isolation
        copied_courses = copy.deepcopy(baseline.courses)
        copied_classrooms = copy.deepcopy(baseline.classrooms)
        copied_time_slots = copy.deepcopy(baseline.time_slots)

        # 4. Remove the specified classroom
        copied_classrooms = [cr for cr in copied_classrooms if cr.id != classroom_id]

        # 6. Construct scenario scoring configuration
        if definition.scoring_config_override:
            scoring_config = copy.deepcopy(definition.scoring_config_override)
        else:
            # Fall back to default config if baseline config wasn't specified explicitly
            scoring_config = copy.deepcopy(baseline.scoring_config) if baseline.scoring_config else ScoringConfig()

        # 7. Construct the EXISTING CSPSolver using copied data
        # We pass max_solutions=1000 to remain consistent with the active dashboard usage,
        # but rely entirely on the native solver API.
        solver = CSPSolver(
            classrooms=copied_classrooms,
            courses=copied_courses,
            time_slots=copied_time_slots,
            max_solutions=1000,
            scoring_config=scoring_config
        )

        # 8. Run solver.solve()
        solver_result = solver.solve()

        # 9-11. Capture result and conditionally validate
        result = ScenarioResult(
            success=solver_result.success,
            solver_result=solver_result,
            allocations=solver_result.allocations,
            score=solver_result.score,
            score_breakdown=solver_result.score_breakdown,
            failure_reasons=solver_result.failure_reasons
        )

        if solver_result.success:
            # 10. Run existing ValidationService
            val_result = ValidationService.validate_allocations(
                allocations=solver_result.allocations,
                all_courses=copied_courses,
                all_time_slots=copied_time_slots
            )
            result.validation_result = val_result

        return result
