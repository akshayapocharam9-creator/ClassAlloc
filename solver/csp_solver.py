import time
import copy
from typing import List, Dict, Tuple, Optional
from models import Classroom, Course, TimeSlot, Allocation
from solver.constraints import satisfies_static_constraints, satisfies_dynamic_constraints
from solver.result import SolverResult, SolverStats
from dataclasses import dataclass
from solver.scoring import Scoring, ScoringConfig

@dataclass
class SolverConfig:
    max_solutions: int = 500

Domain = List[Tuple[Classroom, TimeSlot]]

class CSPSolver:
    def __init__(
        self, 
        classrooms: List[Classroom], 
        courses: List[Course], 
        time_slots: List[TimeSlot], 
        max_solutions: int = None,
        scoring_config: ScoringConfig = None,
        solver_config: SolverConfig = None
    ):
        self.classrooms = classrooms
        self.courses = courses
        self.time_slots = time_slots
        
        # Backward compatibility for max_solutions
        self.solver_config = solver_config or SolverConfig()
        if max_solutions is not None:
            self.solver_config.max_solutions = max_solutions
            
        self.scoring_config = scoring_config or ScoringConfig()
        
        self.stats = SolverStats()
        self.stats.variables_count = len(courses)
        
        self.best_assignment: Optional[Dict[str, Allocation]] = None
        self.best_score = -1.0
        self.best_score_breakdown = {}

    def _domain_heuristic(self, course: Course, cr: Classroom, ts: TimeSlot) -> float:
        score = 0.0
        
        cap_eff = (course.student_count / cr.capacity) * 100.0
        score += cap_eff * self.scoring_config.capacity_efficiency
        
        time_pref, _ = Scoring.calc_time_preference(course.preferred_time_slots, ts.id)
        score += time_pref * self.scoring_config.time_preference
        
        feat_eff, _ = Scoring.calc_feature_efficiency(len(course.required_features), len(cr.features))
        score += feat_eff * self.scoring_config.feature_efficiency
        
        # Timetable quality cannot be evaluated for a single isolated assignment, 
        # so we rely on the other three priorities for initial ordering.
        return score

    def _build_initial_domains(self) -> Dict[str, Domain]:
        domains: Dict[str, Domain] = {}
        for course in self.courses:
            domain = []
            for cr in self.classrooms:
                for ts in self.time_slots:
                    self.stats.constraints_checked += 1
                    if satisfies_static_constraints(course, cr, ts):
                        domain.append((cr, ts))
            
            # Dynamic Heuristic: sort domain by a weighted sum of available priorities
            domain.sort(key=lambda item: self._domain_heuristic(course, item[0], item[1]), reverse=True)
            
            domains[course.id] = domain
            self.stats.initial_domain_sizes[course.id] = len(domain)
        return domains

    def _select_unassigned_variable(self, unassigned: List[Course], domains: Dict[str, Domain]) -> Course:
        # Minimum Remaining Values (MRV)
        return min(unassigned, key=lambda c: len(domains[c.id]))

    def _forward_check(
        self, 
        course: Course, 
        assignment_cr: Classroom, 
        assignment_ts: TimeSlot, 
        unassigned: List[Course], 
        domains: Dict[str, Domain]
    ) -> Optional[Dict[str, Domain]]:
        new_domains = {}
        for other_course in unassigned:
            if other_course.id == course.id:
                continue
            
            pruned_domain = []
            for (cr, ts) in domains[other_course.id]:
                self.stats.constraints_checked += 1
                if cr.id == assignment_cr.id and ts.id == assignment_ts.id:
                    continue
                if other_course.faculty == course.faculty and ts.id == assignment_ts.id:
                    continue
                pruned_domain.append((cr, ts))
                
            if not pruned_domain:
                return None
            new_domains[other_course.id] = pruned_domain
            
        return new_domains

    def _backtrack(
        self, 
        assignment: Dict[str, Allocation], 
        unassigned: List[Course], 
        domains: Dict[str, Domain]
    ) -> bool:
        """
        Returns True if we should stop searching entirely (e.g. max solutions reached).
        """
        if not unassigned:
            self.stats.solutions_explored += 1
            allocs = list(assignment.values())
            score, breakdown = Scoring.evaluate(allocs, self.scoring_config)
            
            if score > self.best_score:
                self.best_score = score
                self.best_score_breakdown = breakdown
                self.best_assignment = copy.deepcopy(assignment)
                
            if self.stats.solutions_explored >= self.solver_config.max_solutions:
                return True
            return False

        course = self._select_unassigned_variable(unassigned, domains)
        unassigned.remove(course)

        for (cr, ts) in domains[course.id]:
            self.stats.assignments_attempted += 1
            
            new_domains = self._forward_check(course, cr, ts, unassigned, domains)
            if new_domains is not None:
                allocation = Allocation(
                    course=course,
                    classroom=cr,
                    time_slot=ts,
                    faculty=course.faculty
                )
                assignment[course.id] = allocation
                
                stop_search = self._backtrack(assignment, unassigned, new_domains)
                
                del assignment[course.id]
                self.stats.backtracks += 1
                
                if stop_search:
                    unassigned.append(course)
                    return True
            else:
                self.stats.backtracks += 1

        unassigned.append(course)
        return False

    def solve(self) -> SolverResult:
        domains = self._build_initial_domains()
        
        failure_reasons = {}
        empty_domains = False
        for c_id, dom in domains.items():
            if not dom:
                empty_domains = True
                failure_reasons[c_id] = "No possible assignments satisfy static constraints."
                
        if empty_domains:
            unallocated = [c for c in self.courses if not domains[c.id]]
            return SolverResult(
                success=False,
                total_courses=len(self.courses),
                unallocated_courses=unallocated,
                failure_reasons=failure_reasons,
                stats=self.stats
            )
            
        unassigned = self.courses.copy()
        assignment: Dict[str, Allocation] = {}
        
        self._backtrack(assignment, unassigned, domains)
        
        if self.best_assignment is not None:
            return SolverResult(
                success=True,
                allocations=list(self.best_assignment.values()),
                total_courses=len(self.courses),
                allocated_count=len(self.best_assignment),
                stats=self.stats,
                score=self.best_score,
                score_breakdown=self.best_score_breakdown
            )
        else:
            return SolverResult(
                success=False,
                total_courses=len(self.courses),
                failure_reasons={"Global": "Constraint network unsatisfiable. Backtracking exhausted all options."},
                stats=self.stats
            )

if __name__ == "__main__":
    from services.data_loader import DataLoader
    loader = DataLoader("data")
    ts, cr, c = loader.load_all()
    solver = CSPSolver(cr, c, ts, max_solutions=1000)
    
    start = time.time()
    result = solver.solve()
    runtime = time.time() - start
    
    print("\n=== ClassAlloc CSP Solver Execution ===")
    print(f"Success: {result.success}")
    print(f"Allocated: {result.allocated_count} / {result.total_courses}")
    print(f"Stats:")
    print(f"  Variables: {result.stats.variables_count}")
    print(f"  Solutions explored: {result.stats.solutions_explored}")
    print(f"  Assignments attempted: {result.stats.assignments_attempted}")
    print(f"  Backtracks: {result.stats.backtracks}")
    print(f"  Constraints checked: {result.stats.constraints_checked}")
    print(f"  Runtime: {runtime:.4f}s")
    
    if result.success:
        print(f"\nOptimization Score: {result.score:.2f} / 100")
        print("Score Breakdown:")
        for k, v in result.score_breakdown.items():
            print(f"  {k}: {v:.2f}")
            
        print("\nAllocations (Best Solution):")
        for alloc in result.allocations:
            print(f"  {alloc.course.id:10} -> {alloc.classroom.id:8} @ {alloc.time_slot.id:12} (Faculty: {alloc.faculty})")
    else:
        print(f"\nFailures:")
        for k, v in result.failure_reasons.items():
            print(f"  {k}: {v}")
