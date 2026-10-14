import streamlit as st
import time
from services.data_loader import DataLoader
from solver.csp_solver import CSPSolver
import ui.dashboard as dashboard
import ui.data_management as data_management

def load_data():
    loader = DataLoader("data")
    ts, cr, c = loader.load_all()
    st.session_state['time_slots'] = ts
    st.session_state['classrooms'] = cr
    st.session_state['courses'] = c
    st.session_state['data_loaded'] = True
    st.session_state['solver_result'] = None
    st.session_state['runtime'] = 0.0

def main():
    st.set_page_config(page_title="ClassAlloc", page_icon="🏫", layout="wide")
    
    # Custom CSS for larger sidebar text
    st.markdown("""
        <style>
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            font-size: 26px !important;
            font-weight: 800 !important;
        }
        [data-testid="stSidebar"] .stRadio p {
            font-size: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.title("🏫 ClassAlloc")
    
    # Initialize session state for persistent data
    if 'data_loaded' not in st.session_state:
        try:
            load_data()
        except Exception as e:
            st.error(f"Failed to load datasets: {e}")
            st.session_state['data_loaded'] = False
            return
            
    if 'solver_result' not in st.session_state:
        st.session_state['solver_result'] = None
        st.session_state['runtime'] = 0.0

    page = st.sidebar.radio(
        "Navigation", 
        [
            "Solver Dashboard", 
            "Analytics & Insights", 
            "What-If Optimization Lab", 
            "Pre-Flight Check", 
            "Data Management",
            "Presentation & Documentation"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **ClassAlloc — University Scheduling**  
    *Constraint Satisfaction Problem (CSP)*  
    **Developer:** Pocharam Akshaya  
    **Course:** FOAI | 2026–27  
    *Woxsen University*
    """)
    
    if page == "Solver Dashboard":
        render_dashboard()
    elif page == "Analytics & Insights":
        import ui.analytics as analytics
        from services.analytics import AnalyticsService
        from services.validation import ValidationService
        result = st.session_state.get('solver_result')
        
        val_result = None
        if result and result.allocations:
            # We can re-run validation easily or fetch it
            c = st.session_state['courses']
            ts = st.session_state['time_slots']
            val_result = ValidationService.validate_allocations(result.allocations, c, ts)
            
        report = AnalyticsService.generate_report(
            allocations=result.allocations if result else [],
            all_courses=st.session_state.get('courses', []),
            all_classrooms=st.session_state.get('classrooms', []),
            all_time_slots=st.session_state.get('time_slots', []),
            solver_result=result,
            validation_result=val_result
        )
        analytics.render_analytics_dashboard(report)
    elif page == "What-If Optimization Lab":
        import ui.what_if as what_if
        what_if.render_what_if_lab()
    elif page == "Pre-Flight Check":
        import ui.preflight as preflight
        preflight.render_preflight_check()
    elif page == "Data Management":
        data_management.render_data_management(load_data)
    elif page == "Presentation & Documentation":
        import ui.presentation_docs as presentation_docs
        presentation_docs.render_presentation_docs()

def render_dashboard():
    # Header
    dashboard.render_header()
    
    ts = st.session_state['time_slots']
    cr = st.session_state['classrooms']
    c = st.session_state['courses']
    
    # Summary Metrics
    dashboard.render_metrics(c, cr, ts, st.session_state['solver_result'])
    
    # Data Overview
    with st.expander("View Loaded Data", expanded=False):
        dashboard.render_data_overview(ts, cr, c)

    st.markdown("---")
    
    # Main Action section
    st.subheader("Solver Engine")
    
    if st.button("Generate Optimal Timetable", type="primary"):
        with st.spinner("Running CSP Solver and Optimizing..."):
            solver = CSPSolver(cr, c, ts, max_solutions=1000)
            
            start = time.time()
            result = solver.solve()
            runtime = time.time() - start
            
            # Cache results in state so UI doesn't reset them
            st.session_state['solver_result'] = result
            st.session_state['runtime'] = runtime
            
    # Conditional Results Rendering
    result = st.session_state['solver_result']
    if result is not None:
        st.markdown("---")
        dashboard.render_results(result, st.session_state['runtime'], cr)

if __name__ == "__main__":
    main()
