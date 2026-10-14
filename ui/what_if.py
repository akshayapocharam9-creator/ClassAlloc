import streamlit as st
import pandas as pd
from typing import Optional

from models.scenario import ScenarioDefinition, ScenarioBaseline, ScenarioResult
from services.scenario_runner import ScenarioRunner
from services.scenario_comparator import ScenarioComparator
from services.analytics import AnalyticsService
from services.validation import ValidationService
from solver.result import SolverResult

def render_what_if_lab():
    st.title("What-If Optimization Lab")
    st.markdown("### Explore hypothetical scheduling changes without modifying the current allocation.")
    
    st.info("Scenarios are isolated simulations. Your current schedule is not modified.")
    
    baseline_result: Optional[SolverResult] = st.session_state.get('solver_result')
    if not baseline_result:
        st.warning("No baseline schedule generated yet. Please generate a schedule on the Solver Dashboard first.")
        return
        
    if not baseline_result.success:
        st.warning("The current baseline schedule is infeasible. What-If comparisons require a feasible baseline.")
        return
        
    classrooms = st.session_state.get('classrooms', [])
    courses = st.session_state.get('courses', [])
    time_slots = st.session_state.get('time_slots', [])
    
    st.markdown("---")
    
    # [Scenario configuration card]
    st.subheader("Scenario Configuration")
    
    # We only support CLASSROOM_OUTAGE in V1
    scenario_type = "CLASSROOM_OUTAGE"
    
    col1, col2 = st.columns(2)
    with col1:
        cr_options = {cr.id: f"{cr.id} - {cr.name}" for cr in classrooms}
        selected_cr_id = st.selectbox("Classroom to remove", options=list(cr_options.keys()), format_func=lambda x: cr_options[x])
        
    # We store the scenario and comparison in session_state specific to what-if, so it doesn't vanish on UI interaction
    if 'what_if_scenario_result' not in st.session_state:
        st.session_state['what_if_scenario_result'] = None
    if 'what_if_comparison' not in st.session_state:
        st.session_state['what_if_comparison'] = None
    if 'what_if_definition' not in st.session_state:
        st.session_state['what_if_definition'] = None
        
    if st.button("Run What-If Scenario", type="primary"):
        definition = ScenarioDefinition(
            name="Classroom Outage Scenario",
            scenario_type=scenario_type,
            hypothetical_changes={"classroom_id": selected_cr_id}
        )
        
        baseline = ScenarioBaseline(
            courses=courses,
            classrooms=classrooms,
            time_slots=time_slots,
            solver_result=baseline_result,
            # we don't have scoring_config in session state, so it remains None (default behavior handles it)
            scoring_config=None
        )
        
        with st.spinner("Running isolated scenario simulation..."):
            scenario_res = ScenarioRunner.run(baseline, definition)
            
            # To run comparison, we optionally need baseline analytics
            val_result = ValidationService.validate_allocations(baseline_result.allocations, courses, time_slots)
            baseline_analytics = AnalyticsService.generate_report(
                allocations=baseline_result.allocations,
                all_courses=courses,
                all_classrooms=classrooms,
                all_time_slots=time_slots,
                solver_result=baseline_result,
                validation_result=val_result
            )
            
            comp = ScenarioComparator.compare(baseline_result, scenario_res, baseline_analytics)
            
            st.session_state['what_if_scenario_result'] = scenario_res
            st.session_state['what_if_comparison'] = comp
            st.session_state['what_if_definition'] = definition

    # Render results if they exist
    scenario_res: Optional[ScenarioResult] = st.session_state.get('what_if_scenario_result')
    comp = st.session_state.get('what_if_comparison')
    definition = st.session_state.get('what_if_definition')
    
    if scenario_res and comp and definition:
        st.markdown("---")
        
        # A. Scenario Summary
        st.subheader("Scenario Summary")
        s_col1, s_col2, s_col3 = st.columns(3)
        s_col1.metric("Scenario Type", definition.scenario_type)
        s_col2.metric("Removed Classroom", definition.hypothetical_changes.get("classroom_id", "N/A"))
        s_col3.metric("Feasibility", "FEASIBLE" if scenario_res.success else "INFEASIBLE", 
                      delta="Unchanged" if not comp.feasibility_changed else ("Declined" if not scenario_res.success else "Improved"),
                      delta_color="off" if not comp.feasibility_changed else ("inverse" if not scenario_res.success else "normal"))

        if not scenario_res.success:
            # 6. INFEASIBLE RESULT
            st.error("Scenario is INFEASIBLE. Constraints cannot be satisfied.")
            st.markdown("#### Failure Information")
            for k, v in scenario_res.failure_reasons.items():
                st.write(f"- **{k}**: {v}")
            return
            
        # B. Optimization Impact
        st.subheader("Optimization Impact")
        o_col1, o_col2, o_col3, o_col4 = st.columns(4)
        o_col1.metric("Baseline Score", f"{comp.baseline_score:.2f}")
        o_col2.metric("Scenario Score", f"{comp.scenario_score:.2f}", 
                      delta=f"{comp.score_delta:+.2f}" if comp.score_delta != 0 else None,
                      delta_color="normal" if comp.score_delta >= 0 else "inverse")
        o_col3.metric("Score Direction", comp.score_direction)
        
        # C. Score Breakdown
        st.markdown("#### Score Breakdown Deltas")
        if comp.breakdown_deltas:
            b_cols = st.columns(len(comp.breakdown_deltas))
            for idx, (metric, delta) in enumerate(comp.breakdown_deltas.items()):
                title = metric.replace("_", " ").title()
                # Find the actual scenario value if possible, else just show delta
                val_str = f"{scenario_res.score_breakdown.get(metric, 0):.2f}"
                b_cols[idx].metric(title, val_str, delta=f"{delta:+.2f}" if delta != 0 else None)
        else:
            st.write("No score breakdown deltas available.")
            
        # E. Impact Summary
        st.markdown("#### Displacement Summary")
        d_col1, d_col2, d_col3 = st.columns(3)
        d_col1.metric("Total Courses Affected", comp.total_courses_affected)
        d_col2.metric("Classroom Changes", comp.courses_classroom_changed)
        d_col3.metric("Time-Slot Changes", comp.courses_time_slot_changed)
        
        # D. Allocation Changes
        st.subheader("Allocation Changes")
        if comp.allocation_changes:
            changes_data = []
            for ac in comp.allocation_changes:
                changes_data.append({
                    "Course": ac.course_id,
                    "Baseline Classroom": ac.baseline_classroom_id or "Unallocated",
                    "Scenario Classroom": ac.scenario_classroom_id or "Unallocated",
                    "Baseline Time": ac.baseline_time_slot_id or "Unallocated",
                    "Scenario Time": ac.scenario_time_slot_id or "Unallocated"
                })
            st.dataframe(pd.DataFrame(changes_data), use_container_width=True)
        else:
            st.success("No courses were displaced. The schedule remained identical aside from the removed resource.")
            
        # F. Analytics Impact
        st.subheader("Analytics Impact")
        if comp.analytics_deltas:
            a_cols = st.columns(3)
            idx = 0
            for metric, delta in comp.analytics_deltas.items():
                if metric in ["allocation_coverage_percentage", "average_capacity_efficiency"]:
                    a_cols[idx % 3].metric(metric.replace("_", " ").title(), f"{delta:+.2f}%")
                elif metric in ["total_teaching_hours"]:
                    a_cols[idx % 3].metric(metric.replace("_", " ").title(), f"{delta:+.2f} hrs")
                else:
                    a_cols[idx % 3].metric(metric.replace("_", " ").title(), f"{delta:+.0f}")
                idx += 1
        else:
            st.write("No analytics deltas computed.")
