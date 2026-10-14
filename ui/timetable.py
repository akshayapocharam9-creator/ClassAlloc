import streamlit as st
from typing import List
from models import Allocation
from services.timetable import TimetableService

def render_timetable_explorer(allocations: List[Allocation]):
    st.subheader("Timetable Explorer")
    
    if not allocations:
        st.info("No allocations generated yet. Please run the solver.")
        return

    days = ["All"] + TimetableService.get_all_days(allocations)
    times = ["All"] + TimetableService.get_all_times(allocations)
    classrooms = ["All"] + TimetableService.get_all_classrooms(allocations)
    faculty = ["All"] + TimetableService.get_all_faculty(allocations)
    sections = ["All"] + TimetableService.get_all_sections(allocations)
    
    has_sections = len(sections) > 1

    tabs = ["University View", "Room View", "Faculty View"]
    if has_sections:
        tabs.append("Section View")
    
    selected_tab = st.tabs(tabs)

    with selected_tab[0]: # University View
        st.markdown("### University Timetable")
        c1, c2, c3, c4 = st.columns(4)
        f_day = c1.selectbox("Filter by Day", days, key="u_day")
        f_time = c2.selectbox("Filter by Time", times, key="u_time")
        f_room = c3.selectbox("Filter by Room", classrooms, key="u_room")
        f_fac = c4.selectbox("Filter by Faculty", faculty, key="u_fac")
        
        f_sec = "All"
        if has_sections:
            f_sec = st.selectbox("Filter by Section", sections, key="u_sec")

        entries = TimetableService.get_university_timetable(
            allocations, 
            day_filter=f_day, 
            time_filter=f_time, 
            classroom_filter=f_room, 
            faculty_filter=f_fac,
            section_filter=f_sec
        )
        _render_entries_table(entries, has_sections, key_prefix="univ")

    with selected_tab[1]: # Room View
        st.markdown("### Room Timetable")
        selected_room = st.selectbox("Select Classroom", classrooms[1:], key="r_room")
        if selected_room:
            entries = TimetableService.get_room_timetable(allocations, selected_room)
            _render_entries_table(entries, has_sections, key_prefix="room")

    with selected_tab[2]: # Faculty View
        st.markdown("### Faculty Timetable")
        selected_fac = st.selectbox("Select Faculty", faculty[1:], key="f_fac")
        if selected_fac:
            entries = TimetableService.get_faculty_timetable(allocations, selected_fac)
            _render_entries_table(entries, has_sections, key_prefix="fac")

    if has_sections:
        with selected_tab[3]: # Section View
            st.markdown("### Section Timetable")
            selected_sec = st.selectbox("Select Section", sections[1:], key="s_sec")
            if selected_sec:
                entries = TimetableService.get_section_timetable(allocations, selected_sec)
                _render_entries_table(entries, has_sections, key_prefix="sec")

def _render_entries_table(entries, has_sections, key_prefix="view"):
    if not entries:
        st.info("No schedule found for the selected filters.")
        return

    data = []
    for e in entries:
        row = {
            "Day": e.day,
            "Time": e.time_str,
            "Course": e.course_name,
            "Faculty": e.faculty,
            "Classroom": e.classroom_name
        }
        if has_sections:
            row["Section"] = e.section if e.section else ""
        data.append(row)

    st.dataframe(data, use_container_width=True, hide_index=True)
    
    with st.expander("Inspect Allocation Details", expanded=False):
        c_names = [e.course_name for e in entries]
        sel_course = st.selectbox("Select Course to Inspect", c_names, key=f"{key_prefix}_inspect_course")
        if sel_course:
            alloc = next((e.allocation for e in entries if e.course_name == sel_course), None)
            if alloc:
                st.markdown(f"**Course:** {alloc.course.name} (Section: {alloc.course.section})")
                st.markdown(f"**Faculty:** {alloc.faculty}")
                st.markdown(f"**Classroom:** {alloc.classroom.name} (Capacity: {alloc.classroom.capacity})")
                st.markdown(f"**Time Slot:** {alloc.time_slot.day.value} {alloc.time_slot.start_time.strftime('%H:%M')} - {alloc.time_slot.end_time.strftime('%H:%M')}")
                st.markdown(f"**Students Enrolled:** {alloc.course.student_count}")
                st.markdown(f"**Capacity Efficiency:** {(alloc.course.student_count / alloc.classroom.capacity)*100:.1f}%")
