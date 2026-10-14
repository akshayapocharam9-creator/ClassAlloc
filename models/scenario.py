from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid

from .course import Course
from .classroom import Classroom
from .time_slot import TimeSlot
from .allocation import Allocation

# We use string annotations or conditional imports if circular dependencies occur,
# but since scenario.py is a leaf model, it is generally safe to import these here.
from solver.scoring import ScoringConfig
from solver.result import SolverResult
from services.validation import ValidationResult
from services.analytics import AnalyticsResult

@dataclass
class ScenarioDefinition:
    """
    Defines the parameters and hypothetical changes for a What-If scenario.
    """
    name: str
    scenario_type: str  # e.g., "WEIGHT_CHANGE", "CLASSROOM_OUTAGE", "ENROLLMENT_SURGE"
    scenario_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hypothetical_changes: Dict[str, Any] = field(default_factory=dict)
    scoring_config_override: Optional[ScoringConfig] = None
    status: str = "DRAFT"  # DRAFT, RUNNING, COMPLETED, FAILED

@dataclass
class ScenarioBaseline:
    """
    The explicitly isolated baseline context required to run and compare a scenario,
    decoupled from the Streamlit UI state.
    """
    courses: List[Course] = field(default_factory=list)
    classrooms: List[Classroom] = field(default_factory=list)
    time_slots: List[TimeSlot] = field(default_factory=list)
    solver_result: Optional[SolverResult] = None
    scoring_config: Optional[ScoringConfig] = None

@dataclass
class ScenarioResult:
    """
    The computed result of a scenario run, housing all generated artifacts.
    """
    success: bool
    solver_result: Optional[SolverResult] = None
    allocations: List[Allocation] = field(default_factory=list)
    score: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    failure_reasons: Dict[str, str] = field(default_factory=dict)
    
    # Generated downstream artifacts
    validation_result: Optional[ValidationResult] = None
    analytics_result: Optional[AnalyticsResult] = None

@dataclass
class AllocationChange:
    course_id: str
    baseline_classroom_id: Optional[str]
    scenario_classroom_id: Optional[str]
    baseline_time_slot_id: Optional[str]
    scenario_time_slot_id: Optional[str]
    classroom_changed: bool
    time_slot_changed: bool

@dataclass
class ScenarioComparison:
    # 1. FEASIBILITY
    baseline_feasible: bool
    scenario_feasible: bool
    feasibility_changed: bool
    
    # 2. OVERALL SCORE
    baseline_score: float
    scenario_score: float
    score_delta: float
    score_direction: str  # "IMPROVED", "DECLINED", "UNCHANGED", "N/A"
    
    # 3. SCORE BREAKDOWN
    breakdown_deltas: Dict[str, float] = field(default_factory=dict)
    
    # 4. ALLOCATION CHANGES
    allocation_changes: List[AllocationChange] = field(default_factory=list)
    
    # 5. DISPLACEMENT SUMMARY
    courses_classroom_changed: int = 0
    courses_time_slot_changed: int = 0
    total_courses_affected: int = 0
    
    # 6. NEW / REMOVED ALLOCATIONS
    newly_allocated_course_ids: List[str] = field(default_factory=list)
    newly_unallocated_course_ids: List[str] = field(default_factory=list)
    
    # 7. FAILURE INFORMATION
    failure_reasons: Dict[str, str] = field(default_factory=dict)
    
    # 8. ANALYTICS
    analytics_deltas: Dict[str, float] = field(default_factory=dict)
