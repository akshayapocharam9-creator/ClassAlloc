# ClassAlloc — Presentation Demo Plan & Speaking Script

**Project Title:** ClassAlloc — University Classroom Allocation System  
**Subtitle:** CSP-Based Intelligent Classroom Scheduling  
**Institution:** Woxsen University | Academic Year 2026–27  
**Time Allocation:** 8 – 10 Minutes Total (Presentation + Live Demonstration + Q&A)

---

## 1. Presentation Structure & Timing Guide

| Phase | Duration | Focus Area | Supporting Screen / Slide |
| :--- | :--- | :--- | :--- |
| **Phase 1: Opening & Context** | 1.5 mins | Real-world problem, NP-hard nature of timetabling, university scale | Slide 1–2 (Title, Motivation, Objectives) |
| **Phase 2: Mathematical Foundation** | 2.0 mins | CSP formulation, Hard vs. Soft constraints, MRV, Forward Checking | Slide 3–4 (CSP Architecture, Algorithm) |
| **Phase 3: Live Application Demo** | 4.0 mins | Pre-Flight → Data Management → Solver Run → Timetables → Analytics → What-If Lab | Live Browser UI (`http://localhost:8501`) |
| **Phase 4: Key Results & Future Scope** | 1.0 min | Execution metrics, constraint satisfaction, future roadmap | Slide 5 (Results, Benchmarks, Future Work) |
| **Phase 5: Viva / Jury Q&A** | 2.0 mins | Answering examiner technical and architectural questions | Q&A Defense Sheet |

---

## 2. Live Demo Click-by-Click Sequence

Ensure your Streamlit app is running at `http://localhost:8501`. Follow this exact live click order:

### Step 1: Pre-Flight Check (Navigation: *Pre-Flight Check*)
1. Click **"Pre-Flight Check"** in the sidebar.
2. Show the instant validation status (Total hours vs. available slot capacity, classroom upper bounds).
3. **What to say:** *"Before burning computation on the solver, our Pre-Flight system deterministically validates whether a feasible schedule is mathematically possible."*

### Step 2: Data Management (Navigation: *Data Management*)
1. Switch to **"Data Management"**.
2. Briefly switch between the tabs: **Courses**, **Classrooms**, and **Time Slots**.
3. Highlight constraints embedded directly into data models:
   - Capacity, Room Type (`Lecture Hall`, `Computer Lab`, `Seminar Hall`).
   - Required Features (`Projector`, `Smart Board`, `Lab Equipment`).
   - Faculty preferences and Student Cohort Sections (`A`, `B`, etc.).

### Step 3: Core Solver Execution (Navigation: *Solver Dashboard*)
1. Navigate to **"Solver Dashboard"**.
2. Point out the summary metric cards: Number of Courses, Classrooms, Time Slots.
3. Click the primary button: **`Generate Optimal Timetable`**.
4. Observe the spinner running CSP with Forward Checking and MRV.
5. Watch the metrics instantly populate:
   - **Status:** Feasible / Optimal
   - **Runtime:** Sub-second (e.g., ~0.15s – 0.4s)
   - **Constraint Violations:** 0 Hard Constraint Violations
   - **Overall Optimization Score:** Capacity + Feature + Preference alignment

### Step 4: Exploring Timetable Views
1. Scroll down to the interactive Schedule Explorer.
2. Switch tabs to demonstrate multi-stakeholder scheduling:
   - **University View:** Complete grid across Monday through Friday.
   - **Room View:** Select room `C1` or `Lab 1` to show zero room collisions.
   - **Faculty View:** Filter by a professor (e.g., `Dr. Smith`) to prove faculty are never scheduled in two rooms at once.
   - **Section View:** Filter by student batch/section to show no student cohort overlaps.

### Step 5: Analytics & Insights (Navigation: *Analytics & Insights*)
1. Click **"Analytics & Insights"** in the sidebar.
2. Point out:
   - **Classroom Utilization Distribution:** Peak vs. off-peak room usage.
   - **Capacity Efficiency Score:** How well classroom sizes match student enrollments (avoiding oversized assignments).
   - **Feature Fit Percentage:** Eliminating waste of specialized lab facilities.

### Step 6: What-If Optimization Lab (Navigation: *What-If Optimization Lab*)
1. Navigate to **"What-If Optimization Lab"**.
2. Explain the scenario: *"Suppose Classroom C1 undergoes unexpected maintenance or AC breakdown tomorrow."*
3. Select `C1` under the **Classroom Outage** scenario.
4. Click **`Run What-If Scenario`**.
5. Show the isolated simulation:
   - The baseline timetable is **never** mutated or overwritten.
   - Clean delta comparison is generated showing affected courses and rescheduled alternatives (or proving infeasibility if capacity is saturated).

---

## 3. Word-for-Word Speaking Script

### Slide 1: Introduction & Motivation
> *"Good morning, respected professors and evaluation panel. Today, I am proud to present **ClassAlloc: A Constraint-Satisfaction-Based Intelligent Classroom Scheduling System**.*
>
> *Every semester, university academic administration faces a massive logistical challenge: allocating hundreds of courses to finite physical classrooms across multiple departments.*
>
> *Manual scheduling or naive greedy algorithms frequently result in double-booked classrooms, faculty timetable clashes, student section overlaps, or severe resource waste—such as putting a 15-student elective into a 150-seat lecture auditorium.*
>
> *Mathematically, university timetabling is an **NP-Hard combinatorial problem**. ClassAlloc replaces error-prone manual spreadsheets with an intelligent, deterministic Constraint Satisfaction Problem (CSP) architecture that guarantees 100% adherence to institutional hard constraints while maximizing soft optimization scores."*

---

### Slide 2: System Architecture & Problem Formulation
> *"To solve this problem, we formulated classroom allocation strictly as a CSP defined by a 3-tuple: **Variables**, **Domains**, and **Constraints**.*
>
> 1. ***Variables ($X$):*** *Each individual course section that requires scheduling.*
> 2. ***Domains ($D$):*** *All valid Cartesian product pairs of physical `(Classroom, TimeSlot)`.*
> 3. ***Hard Constraints (Must Never Be Violated):***
>    - *Room Conflict: No classroom can host two classes at the identical time.*
>    - *Faculty Conflict: No professor can teach two classes simultaneously.*
>    - *Section Conflict: Cohorts of students cannot have conflicting courses.*
>    - *Capacity & Equipment: A classroom must have capacity greater than or equal to student enrollment and must possess all mandatory features like lab equipment or projectors.*
>
> 4. ***Soft Constraints (Optimization Scoring):***
>    - *Capacity Efficiency: Matching classroom size to student count to minimize empty seats.*
>    - *Feature Efficiency: Avoiding the waste of high-spec rooms on general lectures.*
>    - *Faculty Preference: Honoring preferred time slots wherever mathematically possible."*

---

### Slide 3: Algorithmic Innovation (MRV & Forward Checking)
> *"A brute-force search over hundreds of course-room-slot permutations would suffer from combinatorial explosion, requiring billions of iterations.*
>
> *ClassAlloc achieves sub-second execution through two advanced search heuristics:*
>
> 1. ***MRV (Minimum Remaining Values) Heuristic:*** *Instead of choosing courses arbitrarily, the solver prioritizes the most constrained course first—the one with the fewest legal room-slot options. If a course is hard to schedule, we handle it early before options run out.*
> 2. ***Forward Checking:*** *Whenever a course is provisionally assigned to a room and slot, the solver immediately prunes that room and slot from the legal domains of all future competing courses. If any unassigned course's domain drops to zero, the solver prunes the branch immediately without wasteful recursion.*
>
> *This forward-checking backtrack search guarantees that our solver only explores mathematically viable paths."*

---

### Live Demonstration Transition
> *"Let us now transition from theoretical formulation to the live operational application."*
>
> *(Switch to browser at `http://localhost:8501`)*

#### Live Script Step 1: Pre-Flight Feasibility Check
> *"First, we look at the **Pre-Flight Check** module. In academic operations, administrators frequently load invalid data—such as demanding 50 lecture hours in a department that only has 30 available slot-hours. Rather than letting the solver crash or spin fruitlessly, Pre-Flight runs deterministic static analysis in linear time to guarantee initial mathematical feasibility."*

#### Live Script Step 2: Solver Execution
> *(Navigate to 'Solver Dashboard' and click 'Generate Optimal Timetable')*
>
> *"Here on the **Solver Dashboard**, we have our institutional dataset loaded: 11 courses, 10 classrooms, and 35 weekly time slots.*
>
> *I will now click **`Generate Optimal Timetable`**.*
>
> *(Wait ~0.3 seconds for completion)*
>
> *Notice that in just a fraction of a second, the CSP engine completed forward checking, verified every constraint, and computed our optimal schedule with zero hard constraint violations.*
>
> *Below, we can inspect the generated schedule through four customized administrative lenses:*
> - *The **University View** gives the registrar a bird's-eye schedule.*
> - *The **Room View** lets facilities management track room occupancy.*
> - *The **Faculty View** ensures zero faculty overlap and respects individual teaching time slots.*
> - *And the **Section View** ensures that students in Section A never have overlapping mandatory classes."*

#### Live Script Step 3: Analytics & Decision Support
> *(Navigate to 'Analytics & Insights')*
>
> *"Beyond simply generating a valid grid, ClassAlloc provides executive decision intelligence. Our **Analytics & Insights** module reveals utilization distribution, capacity efficiency rates, and faculty workload balances.*
>
> *Administrators can immediately detect whether expensive computer labs are under-utilized, or whether classroom capacities are misaligned with batch enrollments."*

#### Live Script Step 4: What-If Optimization Lab
> *(Navigate to 'What-If Optimization Lab')*
>
> *"Finally, we introduce one of ClassAlloc's most innovative features: the **What-If Optimization Lab**.*
>
> *In reality, campuses face disruptions: an air conditioner breaks down in Hall 101, or a wing is closed for repairs. In traditional systems, fixing one room breaks the entire timetable.*
>
> *In ClassAlloc, administrators can simulate a **Classroom Outage**. The engine creates an isolated deep-copy of the baseline schedule, applies the outage, re-solves via CSP, and presents a differential impact report—all without mutating or corrupting the live institutional schedule."*

---

### Slide 4: Conclusion & Engineering Rigor
> *(Switch back to final presentation slide)*
>
> *"To summarize: ClassAlloc delivers a comprehensive, production-grade scheduling solution:*
> - *Built on proven **CSP with MRV and Forward Checking**.*
> - *Comprehensive test suite: **91 out of 91 automated tests passing**, verifying solver correctness, constraint integrity, analytics reporting, and scenario isolation.*
> - *Complete separation of concerns across clean data models, solver algorithms, analytics services, and interactive Streamlit UI.*
>
> *For future development, we plan to incorporate multi-variable disruptive scenarios, student enrollment waitlist balancing, and automated cross-semester timetable versioning.*
>
> *Thank you. I am now open to your questions."*

---

## 4. Viva / Examiner Q&A Defense Guide

### Q1: Why did you choose CSP instead of Genetic Algorithms (GA) or Machine Learning?
> **Answer:**
> *"Machine Learning requires historical data and is probabilistic; it cannot mathematically guarantee that zero classrooms or professors are double-booked. Genetic Algorithms are heuristic and can get trapped in local optima or take minutes to converge without guaranteeing constraint satisfaction.*
>
> *CSP, on the other hand, is an exact constraint-reasoning paradigm. By using Forward Checking and MRV pruning, CSP guarantees that any returned solution strictly satisfies 100% of institutional hard constraints, while executing deterministically in sub-second time."*

### Q2: What are your exact Hard Constraints versus Soft Constraints?
> **Answer:**
> - ***Hard Constraints (Non-negotiable):***
>   1. **No Room Collisions:** A room can host at most one course per slot.
>   2. **No Faculty Collisions:** A faculty member cannot be in two places at once.
>   3. **No Section Collisions:** Cohorts/sections cannot have concurrent classes.
>   4. **Room Type Match:** Computer labs for lab courses, lecture halls for lectures.
>   5. **Capacity Adequacy:** Room capacity $\ge$ Course student count.
>   6. **Mandatory Features:** Projector, smart board, audio systems.
> - ***Soft Constraints (Optimized via Scoring Function):***
>   1. **Capacity Wastage Minimization:** Penalizing assigning small batches to giant auditoriums.
>   2. **Feature Surplus Minimization:** Avoiding locking specialized rooms for plain courses.
>   3. **Faculty Slot Preferences:** Prioritizing faculty-preferred teaching times.

### Q3: What is the computational complexity, and how do you prevent exponential blowup?
> **Answer:**
> *"In the worst case, general CSP is $O(d^n)$, where $n$ is the number of courses and $d$ is the domain size (Rooms $\times$ Slots). However, our system prevents worst-case exponential growth through two techniques:*
> 1. ***Forward Checking:*** *Prunes inconsistent domain values ahead of time, drastically reducing branching factor.*
> 2. ***MRV (Fail-First) Heuristic:*** *By choosing the variable with the smallest remaining domain first, dead ends are identified immediately near the root of the search tree rather than after deep recursion.*
>
> *Additionally, we bound solutions with a configurable maximum candidate threshold to ensure deterministic execution limits."*

### Q4: How does the What-If Lab ensure the baseline schedule is not corrupted?
> **Answer:**
> *"The What-If engine uses an immutable baseline architecture. When a scenario is executed, the `ScenarioRunner` creates a detached deep copy of all courses, classrooms, and time slots. The hypothetical perturbation (such as removing a classroom) is applied exclusively to the copy. The CSP solver executes in complete isolation, and a `ScenarioComparator` calculates the differential metrics against the unchanged baseline."*

### Q5: How do you know your system is reliable?
> **Answer:**
> *"We maintain a comprehensive automated test suite of **91 automated unit and integration tests** covering every layer:*
> - *CSP search and backtrack correctness.*
> - *Independent constraint validation service.*
> - *Analytics calculations and utilization metrics.*
> - *Scenario runner isolation and comparator logic.*
> - *Data persistence and referential integrity.*
>
> *Every single test passes with zero failures, ensuring industrial reliability."*
