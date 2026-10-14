import streamlit as st
from services.analytics import AnalyticsResult

def render_analytics_dashboard(report: AnalyticsResult):
    st.title("Analytics & Insights")
    
    if report.total_allocations == 0:
        st.info("No generated schedule available. Generate a timetable from the Solver Dashboard to view analytics.")
        return
        
    st.markdown("### Key Performance Indicators")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    kpi1.metric("Allocation Coverage", f"{report.allocation_coverage_percentage:.1f}%")
    kpi2.metric("Average Cap. Efficiency", f"{report.average_capacity_efficiency:.1f}%")
    kpi3.metric("Rooms Used", f"{report.used_classrooms} / {report.total_classrooms}")
    kpi4.metric("Total Teaching Hours", f"{report.total_teaching_hours:.1f}h")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Classroom Utilization")
        cr_data = []
        for cr in report.classroom_analytics:
            cr_data.append({
                "Classroom": cr.classroom_name,
                "Capacity": cr.capacity,
                "Sessions": cr.allocated_sessions,
                "Available": cr.available_sessions,
                "Util %": cr.utilization_percentage,
                "Wasted Seats": cr.wasted_capacity
            })
        
        st.dataframe(
            cr_data,
            use_container_width=True,
            column_config={
                "Util %": st.column_config.ProgressColumn(
                    "Util %",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100
                ),
                "Wasted Seats": st.column_config.NumberColumn(format="%d 🪑")
            },
            hide_index=True
        )

        st.markdown("### Faculty Workload")
        fac_data = []
        for fac in report.faculty_analytics:
            fac_data.append({
                "Faculty": fac.faculty,
                "Sessions": fac.session_count,
                "Teaching Hours": fac.total_teaching_hours
            })
        st.dataframe(
            fac_data,
            use_container_width=True,
            column_config={"Teaching Hours": st.column_config.NumberColumn(format="%.1f h")},
            hide_index=True
        )

    with col2:
        st.markdown("### Time Slot Utilization")
        ts_data = []
        for ts in report.time_slot_analytics:
            ts_data.append({
                "Day": ts.day,
                "Time": ts.time_str,
                "Sessions": ts.allocated_sessions
            })
        st.dataframe(ts_data, use_container_width=True, hide_index=True)

        st.markdown("### Day-wise Schedule")
        day_data = []
        for d in report.day_analytics:
            day_data.append({
                "Day": d.day,
                "Sessions": d.allocated_sessions,
                "Teaching Hours": d.teaching_hours
            })
        st.dataframe(
            day_data,
            use_container_width=True,
            column_config={"Teaching Hours": st.column_config.NumberColumn(format="%.1f h")},
            hide_index=True
        )

        st.markdown("### Schedule Health")
        if report.overall_optimization_score is not None:
            st.metric("Optimization Score", f"{report.overall_optimization_score:.1f} / 100")
        
        if report.validation_status is not None:
            val_icon = "✅" if report.validation_status else "❌"
            st.markdown(f"**Validation Status:** {val_icon} {'Passed' if report.validation_status else 'Failed'}")
            st.markdown(f"**Violations:** {report.validation_violations_count}")
            st.markdown(f"**Passed Rules:** {report.validation_passed_rules_count}")
