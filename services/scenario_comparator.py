from typing import Optional
from solver.result import SolverResult
from services.analytics import AnalyticsResult
from models.scenario import ScenarioResult, ScenarioComparison, AllocationChange

class ScenarioComparator:
    @staticmethod
    def compare(
        baseline: SolverResult,
        scenario: ScenarioResult,
        baseline_analytics: Optional[AnalyticsResult] = None
    ) -> ScenarioComparison:
        
        comp = ScenarioComparison(
            baseline_feasible=baseline.success,
            scenario_feasible=scenario.success,
            feasibility_changed=(baseline.success != scenario.success),
            baseline_score=baseline.score,
            scenario_score=scenario.score,
            score_delta=0.0,
            score_direction="N/A"
        )
        
        # Overall score
        if baseline.success and scenario.success:
            comp.score_delta = scenario.score - baseline.score
            if comp.score_delta > 0.001:
                comp.score_direction = "IMPROVED"
            elif comp.score_delta < -0.001:
                comp.score_direction = "DECLINED"
            else:
                comp.score_direction = "UNCHANGED"
                
        # Breakdown deltas
        if baseline.success and scenario.success:
            for k, b_val in baseline.score_breakdown.items():
                if k in scenario.score_breakdown:
                    s_val = scenario.score_breakdown[k]
                    comp.breakdown_deltas[k] = s_val - b_val
                    
        # Allocation Changes
        b_allocs = {a.course.id: a for a in baseline.allocations}
        s_allocs = {a.course.id: a for a in scenario.allocations}
        
        all_course_ids = set(b_allocs.keys()) | set(s_allocs.keys())
        
        affected_courses = set()
        
        for c_id in all_course_ids:
            in_b = c_id in b_allocs
            in_s = c_id in s_allocs
            
            if in_b and not in_s:
                comp.newly_unallocated_course_ids.append(c_id)
            elif not in_b and in_s:
                comp.newly_allocated_course_ids.append(c_id)
            elif in_b and in_s:
                b_a = b_allocs[c_id]
                s_a = s_allocs[c_id]
                
                cr_changed = (b_a.classroom.id != s_a.classroom.id)
                ts_changed = (b_a.time_slot.id != s_a.time_slot.id)
                
                if cr_changed or ts_changed:
                    affected_courses.add(c_id)
                    
                    if cr_changed:
                        comp.courses_classroom_changed += 1
                    if ts_changed:
                        comp.courses_time_slot_changed += 1
                        
                    comp.allocation_changes.append(AllocationChange(
                        course_id=c_id,
                        baseline_classroom_id=b_a.classroom.id,
                        scenario_classroom_id=s_a.classroom.id,
                        baseline_time_slot_id=b_a.time_slot.id,
                        scenario_time_slot_id=s_a.time_slot.id,
                        classroom_changed=cr_changed,
                        time_slot_changed=ts_changed
                    ))
                    
        comp.total_courses_affected = len(affected_courses)
        
        # Failure Information
        if not scenario.success:
            comp.failure_reasons = scenario.failure_reasons
            
        # Analytics
        if baseline_analytics and scenario.analytics_result:
            b_an = baseline_analytics
            s_an = scenario.analytics_result
            
            comp.analytics_deltas["allocation_coverage_percentage"] = s_an.allocation_coverage_percentage - b_an.allocation_coverage_percentage
            comp.analytics_deltas["average_capacity_efficiency"] = s_an.average_capacity_efficiency - b_an.average_capacity_efficiency
            comp.analytics_deltas["total_teaching_hours"] = s_an.total_teaching_hours - b_an.total_teaching_hours
            comp.analytics_deltas["used_classrooms"] = s_an.used_classrooms - b_an.used_classrooms
            comp.analytics_deltas["unused_classrooms"] = s_an.unused_classrooms - b_an.unused_classrooms
            
        return comp
