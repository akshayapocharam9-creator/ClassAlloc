from dataclasses import dataclass, field
from typing import List, Dict
from models import Allocation, Course

@dataclass
class SolverStats:
    variables_count: int = 0
    initial_domain_sizes: Dict[str, int] = field(default_factory=dict)
    assignments_attempted: int = 0
    backtracks: int = 0
    constraints_checked: int = 0
    solutions_explored: int = 0

@dataclass
class SolverResult:
    success: bool
    allocations: List[Allocation] = field(default_factory=list)
    unallocated_courses: List[Course] = field(default_factory=list)
    total_courses: int = 0
    allocated_count: int = 0
    failure_reasons: Dict[str, str] = field(default_factory=dict)
    stats: SolverStats = field(default_factory=SolverStats)
    score: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)
