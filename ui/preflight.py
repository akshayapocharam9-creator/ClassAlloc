import streamlit as st
from services.preflight import PreflightIntelligence

def render_preflight_check():
    st.title("Schedule Readiness")
    st.markdown("Pre-Flight Intelligence checks for structural feasibility and resource bottlenecks before scheduling.")
    
    courses = st.session_state.get('courses', [])
    classrooms = st.session_state.get('classrooms', [])
    time_slots = st.session_state.get('time_slots', [])
    
    if not courses or not classrooms or not time_slots:
        st.warning("Insufficient data to perform pre-flight check.")
        return
        
    with st.spinner("Analyzing data..."):
        engine = PreflightIntelligence(classrooms, courses, time_slots)
        report = engine.analyze()
        
    st.subheader("Overall Status")
    
    if report.overall_status == "CRITICAL":
        st.error(f"🔴 **CRITICAL**: {report.critical_count} Critical Issues Detected. The solver may be unable to produce a complete schedule.")
    elif report.overall_status == "WARNING":
        st.warning(f"🟠 **WARNING**: {report.warning_count} Warnings. Schedule may be difficult to optimize.")
    else:
        st.success("🟢 **HEALTHY**: No critical issues or warnings detected.")
        
    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 Critical", report.critical_count)
    c2.metric("🟠 Warnings", report.warning_count)
    c3.metric("🟢 Healthy Courses", report.healthy_count)
    
    st.markdown("---")
    
    if report.critical_count > 0:
        st.subheader("🔴 Critical Findings")
        for f in report.findings:
            if f.severity == "CRITICAL":
                with st.expander(f"CRITICAL: {f.entity} - {f.category}", expanded=True):
                    st.markdown(f"**Issue:** {f.message}")
                    st.markdown(f"**Why:** {f.explanation}")
                    st.markdown(f"**Suggested Action:** {f.suggested_action}")
                    
    if report.warning_count > 0:
        st.subheader("🟠 Warnings")
        for f in report.findings:
            if f.severity == "WARNING":
                with st.expander(f"WARNING: {f.entity} - {f.category}", expanded=False):
                    st.markdown(f"**Issue:** {f.message}")
                    st.markdown(f"**Why:** {f.explanation}")
                    st.markdown(f"**Suggested Action:** {f.suggested_action}")
                    
    with st.expander("Healthy Courses Analysis", expanded=False):
        healthy_c = [c for c in report.course_analysis.values() if not c.issues]
        if healthy_c:
            for hc in healthy_c:
                st.markdown(f"- **{hc.course_id}**: {hc.domain_size} possible scheduling combinations.")
        else:
            st.info("No completely healthy courses found.")
            
    if report.bottlenecks:
        st.subheader("Resource Bottlenecks")
        for b in report.bottlenecks:
            st.warning(f"**{b.entity}**: {b.message}")
