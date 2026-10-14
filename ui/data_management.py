import streamlit as st
import datetime
from models import Course, Classroom, TimeSlot, RoomType, Feature, DayOfWeek
from services.data_loader import DataLoader

def render_data_management(reload_callback):
    st.title("Data Management")
    st.markdown("Manage Courses, Classrooms, and Time Slots.")
    
    tab1, tab2, tab3 = st.tabs(["Courses", "Classrooms", "Time Slots"])
    
    with tab1:
        render_courses_tab(reload_callback)
        
    with tab2:
        render_classrooms_tab(reload_callback)
        
    with tab3:
        render_time_slots_tab(reload_callback)

def render_courses_tab(reload_callback):
    st.subheader("Manage Courses")
    
    courses = st.session_state.get('courses', [])
    time_slots = st.session_state.get('time_slots', [])
    loader = DataLoader("data")
    
    c_data = []
    for c in courses:
        c_data.append({
            "ID": c.id,
            "Name": c.name,
            "Faculty": c.faculty,
            "Students": c.student_count,
            "Room Type": c.required_room_type.value
        })
    if c_data:
        st.dataframe(c_data, use_container_width=True)
    else:
        st.info("No courses found.")
        
    action = st.radio("Action", ["Add New Course", "Edit Existing Course", "Delete Course"], horizontal=True, key="c_action")
    
    if action == "Add New Course":
        with st.form("add_course_form"):
            c_id = st.text_input("Course ID")
            c_name = st.text_input("Course Name")
            faculty = st.text_input("Faculty")
            section = st.text_input("Section (Optional)")
            students = st.number_input("Student Count", min_value=0, value=30)
            req_room = st.selectbox("Required Room Type", [r for r in RoomType])
            req_feat = st.multiselect("Required Features", [f for f in Feature])
            pref_ts = st.multiselect("Preferred Time Slots", options=time_slots, format_func=lambda ts: f"{ts.day.value} {ts.start_time.strftime('%H:%M')}")
            
            if st.form_submit_button("Add Course"):
                if not c_id or not c_name or not faculty:
                    st.error("ID, Name, and Faculty are required.")
                elif any(c.id == c_id for c in courses):
                    st.error(f"Course with ID {c_id} already exists.")
                else:
                    new_course = Course(
                        id=c_id,
                        name=c_name,
                        faculty=faculty,
                        student_count=students,
                        required_room_type=req_room,
                        required_features=set(req_feat),
                        preferred_time_slots=pref_ts,
                        section=section if section else None
                    )
                    courses.append(new_course)
                    loader.save_all(st.session_state.get('time_slots', []), st.session_state.get('classrooms', []), courses)
                    reload_callback()
                    st.success("Course added successfully.")
                    st.rerun()
                    
    elif action == "Edit Existing Course":
        if not courses:
            return
        
        course_ids = [c.id for c in courses]
        selected_id = st.selectbox("Select Course", course_ids, format_func=lambda x: f"{x} - {next(c.name for c in courses if c.id == x)}")
        selected_course = next(c for c in courses if c.id == selected_id)
        
        with st.form("edit_course_form"):
            c_name = st.text_input("Course Name", value=selected_course.name)
            faculty = st.text_input("Faculty", value=selected_course.faculty)
            section = st.text_input("Section (Optional)", value=selected_course.section if selected_course.section else "")
            students = st.number_input("Student Count", min_value=0, value=selected_course.student_count)
            
            req_room = st.selectbox("Required Room Type", [r for r in RoomType], index=list(RoomType).index(selected_course.required_room_type))
            req_feat = st.multiselect("Required Features", [f for f in Feature], default=list(selected_course.required_features))
            pref_ts = st.multiselect("Preferred Time Slots", options=time_slots, default=selected_course.preferred_time_slots, format_func=lambda ts: f"{ts.day.value} {ts.start_time.strftime('%H:%M')}")
            
            if st.form_submit_button("Save Changes"):
                if not c_name or not faculty:
                    st.error("Name and Faculty are required.")
                else:
                    new_course = Course(
                        id=selected_id,
                        name=c_name,
                        faculty=faculty,
                        student_count=students,
                        required_room_type=req_room,
                        required_features=set(req_feat),
                        preferred_time_slots=pref_ts,
                        section=section if section else None
                    )
                    
                    # Replace in list safely
                    idx = next(i for i, c in enumerate(courses) if c.id == selected_id)
                    courses[idx] = new_course
                    
                    loader.save_all(st.session_state.get('time_slots', []), st.session_state.get('classrooms', []), courses)
                    reload_callback()
                    st.success("Course updated successfully.")
                    st.rerun()

    elif action == "Delete Course":
        if not courses:
            return
        selected_course = st.selectbox("Select Course to Delete", courses, format_func=lambda c: f"{c.id} - {c.name}")
        st.warning(f"Are you sure you want to delete {selected_course.id}? This action cannot be undone.")
        if st.button("Confirm Delete", type="primary"):
            courses.remove(selected_course)
            loader.save_all(st.session_state.get('time_slots', []), st.session_state.get('classrooms', []), courses)
            reload_callback()
            st.success("Course deleted successfully.")
            st.rerun()

def render_classrooms_tab(reload_callback):
    st.subheader("Manage Classrooms")
    
    classrooms = st.session_state.get('classrooms', [])
    time_slots = st.session_state.get('time_slots', [])
    loader = DataLoader("data")
    
    cr_data = []
    for cr in classrooms:
        cr_data.append({
            "ID": cr.id,
            "Name": cr.name,
            "Building": cr.building,
            "Capacity": cr.capacity,
            "Room Type": cr.room_type.value
        })
    if cr_data:
        st.dataframe(cr_data, use_container_width=True)
    else:
        st.info("No classrooms found.")
        
    action = st.radio("Action", ["Add New Classroom", "Edit Existing Classroom", "Delete Classroom"], horizontal=True, key="cr_action")
    
    if action == "Add New Classroom":
        with st.form("add_classroom_form"):
            cr_id = st.text_input("Classroom ID")
            cr_name = st.text_input("Room Name")
            building = st.text_input("Building")
            capacity = st.number_input("Capacity", min_value=1, value=30)
            room_type = st.selectbox("Room Type", [r for r in RoomType])
            features = st.multiselect("Features", [f for f in Feature])
            avail_ts = st.multiselect("Available Time Slots", options=time_slots, format_func=lambda ts: f"{ts.day.value} {ts.start_time.strftime('%H:%M')}")
            
            if st.form_submit_button("Add Classroom"):
                if not cr_id or not cr_name or not building:
                    st.error("ID, Name, and Building are required.")
                elif any(cr.id == cr_id for cr in classrooms):
                    st.error(f"Classroom with ID {cr_id} already exists.")
                else:
                    new_cr = Classroom(
                        id=cr_id,
                        name=cr_name,
                        building=building,
                        capacity=capacity,
                        room_type=room_type,
                        features=set(features),
                        available_time_slots=avail_ts
                    )
                    classrooms.append(new_cr)
                    loader.save_all(st.session_state.get('time_slots', []), classrooms, st.session_state.get('courses', []))
                    reload_callback()
                    st.success("Classroom added successfully.")
                    st.rerun()
                    
    elif action == "Edit Existing Classroom":
        if not classrooms:
            return
            
        cr_ids = [cr.id for cr in classrooms]
        selected_id = st.selectbox("Select Classroom", cr_ids, format_func=lambda x: f"{x} - {next(cr.name for cr in classrooms if cr.id == x)}")
        selected_cr = next(cr for cr in classrooms if cr.id == selected_id)
        
        with st.form("edit_classroom_form"):
            cr_name = st.text_input("Room Name", value=selected_cr.name)
            building = st.text_input("Building", value=selected_cr.building)
            capacity = st.number_input("Capacity", min_value=1, value=selected_cr.capacity)
            
            room_type = st.selectbox("Room Type", [r for r in RoomType], index=list(RoomType).index(selected_cr.room_type))
            features = st.multiselect("Features", [f for f in Feature], default=list(selected_cr.features))
            avail_ts = st.multiselect("Available Time Slots", options=time_slots, default=selected_cr.available_time_slots, format_func=lambda ts: f"{ts.day.value} {ts.start_time.strftime('%H:%M')}")
            
            if st.form_submit_button("Save Changes"):
                if not cr_name or not building:
                    st.error("Name and Building are required.")
                else:
                    new_cr = Classroom(
                        id=selected_id,
                        name=cr_name,
                        building=building,
                        capacity=capacity,
                        room_type=room_type,
                        features=set(features),
                        available_time_slots=avail_ts
                    )
                    
                    idx = next(i for i, cr in enumerate(classrooms) if cr.id == selected_id)
                    classrooms[idx] = new_cr
                    
                    loader.save_all(st.session_state.get('time_slots', []), classrooms, st.session_state.get('courses', []))
                    reload_callback()
                    st.success("Classroom updated successfully.")
                    st.rerun()

    elif action == "Delete Classroom":
        if not classrooms:
            return
        selected_cr = st.selectbox("Select Classroom to Delete", classrooms, format_func=lambda cr: f"{cr.id} - {cr.name}")
        st.warning(f"Are you sure you want to delete {selected_cr.id}? This action cannot be undone.")
        if st.button("Confirm Delete", type="primary", key="cr_del"):
            classrooms.remove(selected_cr)
            loader.save_all(st.session_state.get('time_slots', []), classrooms, st.session_state.get('courses', []))
            reload_callback()
            st.success("Classroom deleted successfully.")
            st.rerun()

def render_time_slots_tab(reload_callback):
    st.subheader("Manage Time Slots")
    
    time_slots = st.session_state.get('time_slots', [])
    loader = DataLoader("data")
    
    ts_data = []
    for ts in time_slots:
        ts_data.append({
            "ID": ts.id,
            "Day": ts.day.value,
            "Start": ts.start_time.strftime("%H:%M"),
            "End": ts.end_time.strftime("%H:%M")
        })
    if ts_data:
        st.dataframe(ts_data, use_container_width=True)
    else:
        st.info("No time slots found.")
        
    action = st.radio("Action", ["Add New Time Slot", "Edit Existing Time Slot", "Delete Time Slot"], horizontal=True, key="ts_action")
    
    if action == "Add New Time Slot":
        with st.form("add_ts_form"):
            ts_id = st.text_input("Time Slot ID")
            day = st.selectbox("Day of Week", [d for d in DayOfWeek])
            
            c1, c2 = st.columns(2)
            start_t = c1.time_input("Start Time", value=datetime.time(9, 0))
            end_t = c2.time_input("End Time", value=datetime.time(10, 0))
            
            if st.form_submit_button("Add Time Slot"):
                if not ts_id:
                    st.error("ID is required.")
                elif any(t.id == ts_id for t in time_slots):
                    st.error(f"Time Slot with ID {ts_id} already exists.")
                elif start_t >= end_t:
                    st.error("Start time must be strictly before end time.")
                else:
                    new_ts = TimeSlot(
                        id=ts_id,
                        day=day,
                        start_time=start_t,
                        end_time=end_t
                    )
                    time_slots.append(new_ts)
                    loader.save_all(time_slots, st.session_state.get('classrooms', []), st.session_state.get('courses', []))
                    reload_callback()
                    st.success("Time Slot added successfully.")
                    st.rerun()
                    
    elif action == "Edit Existing Time Slot":
        if not time_slots:
            return
            
        ts_ids = [ts.id for ts in time_slots]
        selected_id = st.selectbox("Select Time Slot", ts_ids, format_func=lambda x: next(f"{t.id} - {t.day.value} {t.start_time.strftime('%H:%M')}" for t in time_slots if t.id == x))
        selected_ts = next(t for t in time_slots if t.id == selected_id)
        
        with st.form("edit_ts_form"):
            day = st.selectbox("Day of Week", [d for d in DayOfWeek], index=list(DayOfWeek).index(selected_ts.day))
            
            c1, c2 = st.columns(2)
            start_t = c1.time_input("Start Time", value=selected_ts.start_time)
            end_t = c2.time_input("End Time", value=selected_ts.end_time)
            
            if st.form_submit_button("Save Changes"):
                if start_t >= end_t:
                    st.error("Start time must be strictly before end time.")
                else:
                    new_ts = TimeSlot(
                        id=selected_id,
                        day=day,
                        start_time=start_t,
                        end_time=end_t
                    )
                    
                    idx = next(i for i, t in enumerate(time_slots) if t.id == selected_id)
                    time_slots[idx] = new_ts
                    
                    courses = st.session_state.get('courses', [])
                    classrooms = st.session_state.get('classrooms', [])
                    
                    for c in courses:
                        if selected_ts in c.preferred_time_slots:
                            c.preferred_time_slots = [new_ts if t == selected_ts else t for t in c.preferred_time_slots]
                            
                    for cr in classrooms:
                        if selected_ts in cr.available_time_slots:
                            cr.available_time_slots = [new_ts if t == selected_ts else t for t in cr.available_time_slots]
                            
                    loader.save_all(time_slots, classrooms, courses)
                    reload_callback()
                    st.success("Time Slot updated successfully.")
                    st.rerun()

    elif action == "Delete Time Slot":
        if not time_slots:
            return
        selected_ts = st.selectbox("Select Time Slot to Delete", time_slots, format_func=lambda t: f"{t.id} - {t.day.value} {t.start_time.strftime('%H:%M')}")
        
        courses = st.session_state.get('courses', [])
        classrooms = st.session_state.get('classrooms', [])
        
        referenced_by_courses = [c.id for c in courses if selected_ts in c.preferred_time_slots]
        referenced_by_classrooms = [cr.id for cr in classrooms if selected_ts in cr.available_time_slots]
        
        if referenced_by_courses or referenced_by_classrooms:
            st.warning("This Time Slot is currently referenced by:")
            if referenced_by_courses:
                st.write(f"- Courses: {', '.join(referenced_by_courses)}")
            if referenced_by_classrooms:
                st.write(f"- Classrooms: {', '.join(referenced_by_classrooms)}")
            st.error("Cannot delete a Time Slot that is in use. Please remove it from the respective courses/classrooms first.")
        else:
            if st.button("Confirm Delete", type="primary", key="ts_del"):
                time_slots.remove(selected_ts)
                loader.save_all(time_slots, st.session_state.get('classrooms', []), st.session_state.get('courses', []))
                reload_callback()
                st.success("Time Slot deleted successfully.")
                st.rerun()
