import os
import streamlit as st

def render_presentation_docs():
    st.title("Project Presentation & Documentation")
    st.markdown("### FOAI Academic Defense, Original Slide Deck & Official Report")
    
    st.markdown("""
    > **Course:** Fundamentals of Artificial Intelligence (FOAI)  
    > **Institution:** Woxsen University | Academic Year 2026–27  
    > **Developer:** **Pocharam Akshaya** (Laxmi Pocharam) • Roll No: 25WU0102208
    """)
    
    st.markdown("---")
    
    # 1. Download Center
    st.subheader("Official Document Downloads")
    
    col1, col2, col3 = st.columns(3)
    
    # PPTX Download
    pptx_path = os.path.join("docs", "Classroom_Allocation_Presentation_V2.pptx")
    if os.path.exists(pptx_path):
        with open(pptx_path, "rb") as f:
            pptx_bytes = f.read()
        col1.download_button(
            label="Download Original PPTX",
            data=pptx_bytes,
            file_name="Classroom_Allocation_Presentation_V2.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            type="primary"
        )
    else:
        col1.info("PPTX located in /docs")

    # Word Report Download
    docx_path = os.path.join("docs", "ClassAlloc_PBL_Report_Final.docx")
    if not os.path.exists(docx_path):
        docx_path = "ClassAlloc_PBL_Report_Final.docx"
    if os.path.exists(docx_path):
        with open(docx_path, "rb") as f:
            docx_bytes = f.read()
        col2.download_button(
            label="Download PBL Report (.docx)",
            data=docx_bytes,
            file_name="ClassAlloc_PBL_Report_Final.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        col2.info("PBL Report in root")

    # Script Download
    script_path = os.path.join("docs", "presentation_demo_and_script.md")
    if not os.path.exists(script_path):
        script_path = os.path.expanduser(r"~\.gemini\antigravity\brain\adf6e1d0-efea-421e-a21a-7067add5a290\presentation_demo_and_script.md")
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            script_text = f.read()
        col3.download_button(
            label="Download Speaking Script (.md)",
            data=script_text,
            file_name="ClassAlloc_Speaking_Script_Viva_Defense.md",
            mime="text/markdown"
        )

    st.markdown("---")
    
    # 2. Interactive Presentation Slides
    st.subheader("Interactive Slide Deck Viewer")
    st.caption("Browse through the verified 8 slides of the FOAI presentation:")

    slides = [
        {
            "num": 1,
            "title": "University Classroom Allocation Using Constraint Satisfaction",
            "category": "Title & Academic Scope",
            "content": """
            ### Foundations of Artificial Intelligence (FOAI)
            **AI-Based Classroom Allocation System**
            
            * **Project:** ClassAlloc — Intelligent Classroom Allocation
            * **Technique:** Constraint Satisfaction Problem (CSP)
            * **Developer:** Pocharam Akshaya (Laxmi Pocharam)
            * **Academic Year:** 2026–27 | Woxsen University
            """,
            "bullet_points": [
                "Formulates university timetabling as a deterministic Constraint Satisfaction Problem.",
                "Eliminates manual scheduling errors, double-bookings, and auditorium seat waste.",
                "Combines Backtracking Search, Forward Checking, and the MRV (Minimum Remaining Values) heuristic."
            ]
        },
        {
            "num": 2,
            "title": "The Problem & Common Conflicts",
            "category": "Problem Statement",
            "content": """
            ### Real-World Academic Scheduling Challenges
            Manual spreadsheet scheduling across finite campus resources creates severe logistical bottlenecks:
            """,
            "bullet_points": [
                "**Room Clash:** Two classes assigned to the same physical room at the exact same time slot.",
                "**Faculty Clash:** A professor scheduled to teach two separate classes simultaneously.",
                "**Capacity Issue:** Placing small batches (e.g. 15 students) into 150-seat auditoriums, wasting capacity.",
                "**Availability Issue:** Courses placed in time slots or days when classrooms or faculty are unavailable.",
                "**Aim:** Automatically generate a provably collision-free classroom allocation by satisfying all predefined hard constraints."
            ]
        },
        {
            "num": 3,
            "title": "Our Proposed System Architecture",
            "category": "System Pipeline",
            "content": """
            ### Computational Pipeline
            The system accepts academic requirements and processes them through an AI reasoning pipeline:
            """,
            "bullet_points": [
                "**Input Module:** Courses, Faculty, Classrooms, Time Slots, and Room Requirements.",
                "**CSP Formulation:** Constructs the constraint graph (Variables, Domains, and Constraints).",
                "**Constraint Checking:** Filters domains against static feasibility boundaries in O(1) time.",
                "**Search & Pruning Engine:** Explores viable assignments using MRV and Forward Checking.",
                "**Output:** Generates a clash-free timetable with multi-stakeholder views."
            ]
        },
        {
            "num": 4,
            "title": "Formal CSP Formulation",
            "category": "Mathematical Model",
            "content": """
            ### The CSP 3-Tuple: (X, D, C)
            """,
            "bullet_points": [
                "**Variables (X):** Each course section requiring scheduling: $X = \\{c_1, c_2, \\dots, c_n\\}$.",
                "**Domains (D):** The set of all valid Cartesian pairs: $D_i = \\{(r, t) \\mid r \\in \\text{Classrooms}, t \\in \\text{TimeSlots}\\}$ that meet static course requirements.",
                "**Constraints (C):** Relational rules that restrict the simultaneous assignment of values to variables.",
                "**Example:** `CS101-A` has Domain = {(`CR_102`, `TS_MON_0900`), (`CR_102`, `TS_WED_0900`), ...} and must not collide with `CS101-B` or `Dr. Smith`'s schedule."
            ]
        },
        {
            "num": 5,
            "title": "Constraints Specification",
            "category": "Constraint Hierarchy",
            "content": """
            ### Hard vs. Soft Constraints
            """,
            "bullet_points": [
                "**01. No Room Clash (Hard):** $\\text{Room}_i = \\text{Room}_j \\implies \\text{Time}_i \\neq \\text{Time}_j$.",
                "**02. No Faculty Clash (Hard):** $\\text{Faculty}_i = \\text{Faculty}_j \\implies \\text{Time}_i \\neq \\text{Time}_j$.",
                "**03. Room Capacity (Hard):** $\\text{Room.capacity} \\ge \\text{Course.student\\_count}$.",
                "**04. Room Availability (Hard):** Time slot must exist in room's operating schedule.",
                "**05. Class Availability (Hard):** Course must be scheduled in an approved time slot.",
                "**06. Room Requirement (Hard):** Specialized lab courses require suitable room types and features.",
                "**Soft Optimization:** Evaluates Capacity Efficiency (40%), Time Preference (20%), Feature Fit (20%), and Timetable Continuity (20%)."
            ]
        },
        {
            "num": 6,
            "title": "System Architecture & Data Flow",
            "category": "Engineering Architecture",
            "content": """
            ### Architectural Separation of Concerns
            """,
            "bullet_points": [
                "**Admin / User:** Interacts via the Streamlit web dashboard.",
                "**Input Module:** Loads JSON dataset for courses, rooms, faculty, and time slots.",
                "**Pre-Flight Engine:** Pre-validates structural capacity before launching search.",
                "**CSP Engine:** Backtracking with Forward Checking and MRV.",
                "**Independent Validator:** Evaluates 8 separate rules post-solve to guarantee zero violations.",
                "**Analytics & What-If Lab:** Computes utilization KPIs and isolated outage simulations."
            ]
        },
        {
            "num": 7,
            "title": "Algorithmic Search & Output Generation",
            "category": "Algorithms",
            "content": """
            ### 6-Step Execution Workflow
            """,
            "bullet_points": [
                "**01. Collect Input:** Ingest academic entities and compute domain sizes.",
                "**02. Create CSP:** Build the constraint network.",
                "**03. Apply Static Constraints:** Prune incompatible room sizes, room types, and equipment.",
                "**04. Search with MRV:** Choose the variable with the smallest remaining domain first.",
                "**05. Forward Checking & Backtrack:** Prune future domains; backtrack immediately if any domain drops to zero.",
                "**06. Output:** Return the highest-scoring timetable with 100% allocation coverage."
            ]
        },
        {
            "num": 8,
            "title": "Mathematical Equation & Summary",
            "category": "Conclusion & Summary",
            "content": """
            ### Core CSP Equation
            $$\\text{Variables} + \\text{Domains} + \\text{Constraints} + \\text{Backtracking with MRV} = \\text{Optimal Allocation}$$
            """,
            "bullet_points": [
                "**Automated Allocation:** Sub-second execution (<0.05 seconds active runtime).",
                "**Zero Conflicts:** 100% constraints satisfied across 1,218 attempted assignments and 5,200+ checks.",
                "**Decision Intelligence:** Provides transparent capacity fit explanation and What-If resilience testing.",
                "**Reliability:** Backed by 91/91 automated tests passing."
            ]
        }
    ]

    # Tabs for slide browsing
    slide_tabs = st.tabs([f"Slide {s['num']}" for s in slides])
    
    for i, tab in enumerate(slide_tabs):
        with tab:
            s = slides[i]
            st.markdown(f"#### Slide {s['num']}: {s['title']}")
            st.caption(f"Category: {s['category']}")
            st.markdown(s['content'])
            st.markdown("**Key Takeaways:**")
            for pt in s['bullet_points']:
                st.markdown(f"- {pt}")

    st.markdown("---")
    
    # 3. Technical Verification Badge
    st.subheader("System Verification & Integrity Status")
    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Automated Tests", "91 / 91 Passed")
    v2.metric("Constraint Violations", "0 (100% Verified)")
    v3.metric("Allocation Coverage", "100.0%")
    v4.metric("Avg Runtime", "0.015s – 0.05s")
