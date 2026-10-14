import streamlit as st
from typing import List, Dict
from models import TimeSlot, Classroom, Course, Allocation
from solver.result import SolverResult

def render_header():
    st.title("ClassAlloc")
    st.markdown("### University Classroom Allocation System")
    st.markdown("**CSP-Based Intelligent Classroom Scheduling**")
    st.markdown("> Automatically allocate university courses to classrooms and time slots while satisfying hard constraints and optimizing timetable quality.")

def render_metrics(courses, classrooms, time_slots, result: SolverResult):
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Total Courses", len(courses))
    col2.metric("Total Classrooms", len(classrooms))
    col3.metric("Available Time Slots", len(time_slots))
    
    if result:
        col4.metric("Allocated", f"{result.allocated_count} / {result.total_courses}")
        col5.metric("Optimization Score", f"{result.score:.1f}/100" if result.success else "N/A")
    else:
        col4.metric("Allocated", "Not run")
        col5.metric("Optimization Score", "Not run")

def render_data_overview(ts, cr, c):
    tab1, tab2, tab3 = st.tabs(["Courses", "Classrooms", "Time Slots"])
    
    with tab1:
        c_data = []
        for course in c:
            c_data.append({
                "Course": course.name,
                "Section": course.section,
                "Faculty": course.faculty,
                "Students": course.student_count,
                "Req. Type": course.required_room_type.value,
                "Req. Features": ", ".join([f.value for f in course.required_features])
            })
        st.dataframe(c_data, use_container_width=True)
        
    with tab2:
        cr_data = []
        for room in cr:
            cr_data.append({
                "Room": room.name,
                "Building": room.building,
                "Capacity": room.capacity,
                "Type": room.room_type.value,
                "Features": ", ".join([f.value for f in room.features])
            })
        st.dataframe(cr_data, use_container_width=True)
        
    with tab3:
        ts_data = []
        for t in ts:
            ts_data.append({
                "ID": t.id,
                "Day": t.day.value,
                "Start": t.start_time.strftime("%H:%M"),
                "End": t.end_time.strftime("%H:%M")
            })
        st.dataframe(ts_data, use_container_width=True)

def sort_allocations(allocations: List[Allocation]) -> List[Allocation]:
    day_order = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}
    return sorted(allocations, key=lambda a: (
        day_order.get(a.time_slot.day.value, 99),
        a.time_slot.start_time,
        a.classroom.name,
        a.course.name
    ))

def render_results(result: SolverResult, runtime: float, classrooms: List[Classroom]):
    if not result.success and not result.allocations:
        st.error("Solver failed to find a complete solution.")
        render_unallocated(result.unallocated_courses, result.failure_reasons)
        return
        
    allocs = sort_allocations(result.allocations)
    
    st.markdown("---")
    from ui.timetable import render_timetable_explorer
    render_timetable_explorer(allocs)
    st.markdown("---")
    
    from services.schedule_explanation import ScheduleExplainer
    expl = ScheduleExplainer.explain(allocs)
    
    with st.expander("Allocation Scoring Details", expanded=False):
        expl_data = []
        for ax in expl.allocations:
            expl_data.append({
                "Course": ax.course_id,
                "Faculty": ax.faculty,
                "Room": ax.room_name,
                "Time": ax.time_str,
                "Students": ax.student_count,
                "Capacity": ax.capacity,
                "Cap Eff %": ax.cap_eff,
                "Time Score": ax.time_pref_score,
                "Feat Score": ax.feat_eff
            })
        st.dataframe(
            expl_data,
            use_container_width=True,
            column_config={
                "Cap Eff %": st.column_config.NumberColumn(format="%.1f%%"),
                "Time Score": st.column_config.NumberColumn(format="%.1f"),
                "Feat Score": st.column_config.NumberColumn(format="%.1f")
            },
            hide_index=True
        )
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Optimization Score")
        st.metric("Overall Score", f"{result.score:.2f} / 100")
        
        b = result.score_breakdown
        
        def safe_prog(val):
            return max(0, min(100, int(val)))
            
        cap_val = b.get('capacity_efficiency', 0)
        st.markdown(f"**Capacity Efficiency** — {cap_val:.2f}%")
        st.progress(safe_prog(cap_val))
        
        time_val = b.get('time_preference', 0)
        st.markdown(f"**Time Preference** — {time_val:.2f}%")
        st.progress(safe_prog(time_val))
        
        feat_val = b.get('feature_efficiency', 0)
        st.markdown(f"**Feature Efficiency** — {feat_val:.2f}%")
        st.progress(safe_prog(feat_val))
        
        qual_val = b.get('timetable_quality', 0)
        st.markdown(f"**Timetable Quality** — {qual_val:.2f}%")
        st.progress(safe_prog(qual_val))
        
        st.markdown("---")
        st.markdown("#### Why this score?")
        
        with st.expander("Capacity Efficiency ▼", expanded=False):
            st.markdown(f"**Aggregate Score: {cap_val:.2f}%**")
            st.markdown("Largest losses:")
            cap_losses = [a for a in expl.allocations if a.cap_eff < 100.0]
            cap_losses.sort(key=lambda x: x.cap_eff)
            for i, a in enumerate(cap_losses[:5]):
                st.markdown(f"{i+1}. **{a.course_id}**\n   {a.student_count} students / {a.capacity} seats\n   Efficiency: {a.cap_eff:.2f}%")
                
        with st.expander("Time Preference ▼", expanded=False):
            st.markdown(f"**Aggregate Score: {time_val:.2f}%**")
            time_losses = [a for a in expl.allocations if a.time_pref_score < 100.0]
            time_losses.sort(key=lambda x: x.time_pref_score)
            for i, a in enumerate(time_losses[:5]):
                st.markdown(f"{i+1}. **{a.course_id}** (Faculty: {a.faculty})\n   {a.time_pref_details}\n   Score: {a.time_pref_score:.2f}")

        with st.expander("Feature Efficiency ▼", expanded=False):
            st.markdown(f"**Aggregate Score: {feat_val:.2f}%**")
            feat_losses = [a for a in expl.allocations if a.feat_eff < 100.0]
            feat_losses.sort(key=lambda x: x.feat_eff)
            for i, a in enumerate(feat_losses[:5]):
                st.markdown(f"{i+1}. **{a.course_id}** (Room: {a.room_name})\n   {a.feat_details}\n   Efficiency: {a.feat_eff:.2f}%")

        with st.expander("Timetable Quality ▼", expanded=False):
            st.markdown(f"**Aggregate Score: {qual_val:.2f}%**")
            qual_losses = [tq for tq in expl.timetable_qualities if tq.score < 100.0]
            qual_losses.sort(key=lambda x: x.score)
            for i, tq in enumerate(qual_losses[:5]):
                st.markdown(f"{i+1}. **{tq.faculty} / {tq.day}**\n   {tq.details}\n   Timetable Quality impact: {tq.score:.2f}%")

        if expl.top_losses:
            st.markdown("#### Largest Optimization Losses")
            for i, loss in enumerate(expl.top_losses[:5]):
                st.markdown(f"{i+1}. **{loss['category']}** — {loss['entity']}\n   *{loss['desc']}*")
        
    with col2:
        st.subheader("Solver Insights")
        s = result.stats
        
        m1, m2 = st.columns(2)
        m1.metric("Variables (Courses)", s.variables_count)
        m2.metric("Solutions Explored", s.solutions_explored)
        
        m3, m4 = st.columns(2)
        m3.metric("Assignments Attempted", f"{s.assignments_attempted:,}")
        m4.metric("Backtracks Triggered", f"{s.backtracks:,}")
        
        m5, m6 = st.columns(2)
        m5.metric("Constraints Checked", f"{s.constraints_checked:,}")
        m6.metric("Execution Runtime", f"{runtime:.4f}s")
        
    st.markdown("---")
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Constraint Validation")
        from services.validation import ValidationService
        courses = st.session_state.get('courses', [])
        time_slots = st.session_state.get('time_slots', [])
        validation_result = ValidationService.validate_allocations(allocs, courses, time_slots)
        
        if validation_result.valid:
            st.success("✅ **100% Constraints Verified Successfully**")
        else:
            st.error(f"❌ **{len([v for v in validation_result.violations if v.severity == 'ERROR'])} Constraint Violations Detected**")
            
        v_col1, v_col2 = st.columns(2)
        idx = 0
        for rule in validation_result.passed_rules:
            target_col = v_col1 if idx % 2 == 0 else v_col2
            target_col.markdown(f"✅ {rule}")
            idx += 1
            
        if validation_result.violations:
            st.markdown("#### Violation Details")
            for v in validation_result.violations:
                icon = "❌" if v.severity == "ERROR" else "⚠️"
                with st.expander(f"{icon} {v.rule_name}"):
                    st.markdown(v.explanation)
                    if v.involved_allocations:
                        st.markdown("**Involved Allocations:**")
                        for a in v.involved_allocations:
                            st.markdown(f"- {a.course.name} (Room: {a.classroom.name}, Time: {a.time_slot.day.value} {a.time_slot.start_time.strftime('%H:%M')})")
            
    with col4:
        st.subheader("Classroom Utilization")
        render_classroom_utilization(classrooms, allocs)

    if result.unallocated_courses:
        render_unallocated(result.unallocated_courses, result.failure_reasons)
    else:
        st.success("All courses successfully allocated.")


def render_classroom_utilization(classrooms: List[Classroom], allocations: List[Allocation]):
    from services.analytics import AnalyticsService
    courses = st.session_state.get('courses', [])
    ts = st.session_state.get('time_slots', [])
    
    report = AnalyticsService.generate_report(allocations, courses, classrooms, ts)
    
    util_data = []
    for cr in report.classroom_analytics:
        util_data.append({
            "Room": cr.classroom_name,
            "Capacity": cr.capacity,
            "Courses Assigned": cr.allocated_sessions
        })
        
    st.dataframe(
        util_data, 
        use_container_width=True,
        column_config={
            "Courses Assigned": st.column_config.ProgressColumn(
                "Courses Assigned",
                help="Number of classes scheduled in this room",
                format="%d classes",
                min_value=0,
                max_value=max(1, len(ts))
            ),
            "Capacity": st.column_config.NumberColumn(
                "Capacity",
                format="%d 🪑"
            )
        },
        hide_index=True
    )

def render_unallocated(unallocated: List[Course], failure_reasons: Dict[str, str]):
    st.warning("Some courses could not be allocated.")
    fail_data = []
    for c in unallocated:
        fail_data.append({
            "Course": c.name,
            "Reason": failure_reasons.get(c.id, "Constraint conflict during search")
        })
    st.table(fail_data)
