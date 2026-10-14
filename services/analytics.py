from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from models import Allocation, Course, Classroom, TimeSlot
from solver.result import SolverResult
from services.validation import ValidationResult
from solver.scoring import Scoring
import datetime

@dataclass
class ClassroomAnalytics:
    classroom_id: str
    classroom_name: str
    room_type: str
    capacity: int
    allocated_sessions: int
    available_sessions: int
    utilization_percentage: float
    wasted_capacity: int

@dataclass
class FacultyAnalytics:
    faculty: str
    session_count: int
    total_teaching_hours: float

@dataclass
class TimeSlotAnalytics:
    time_slot_id: str
    day: str
    time_str: str
    allocated_sessions: int

@dataclass
class DayAnalytics:
    day: str
    allocated_sessions: int
    teaching_hours: float

@dataclass
class AnalyticsResult:
    total_courses: int = 0
    allocated_courses: int = 0
    unallocated_courses: int = 0
    allocation_coverage_percentage: float = 0.0
    
    total_classrooms: int = 0
    used_classrooms: int = 0
    unused_classrooms: int = 0
    
    total_allocations: int = 0
    total_teaching_hours: float = 0.0
    average_capacity_efficiency: float = 0.0
    
    classroom_analytics: List[ClassroomAnalytics] = field(default_factory=list)
    faculty_analytics: List[FacultyAnalytics] = field(default_factory=list)
    time_slot_analytics: List[TimeSlotAnalytics] = field(default_factory=list)
    day_analytics: List[DayAnalytics] = field(default_factory=list)
    
    overall_optimization_score: Optional[float] = None
    validation_status: Optional[bool] = None
    validation_violations_count: Optional[int] = None
    validation_passed_rules_count: Optional[int] = None


class AnalyticsService:
    @staticmethod
    def _calculate_hours(start: datetime.time, end: datetime.time) -> float:
        # Convert times to hours
        start_h = start.hour + start.minute / 60.0
        end_h = end.hour + end.minute / 60.0
        return max(0.0, end_h - start_h)

    @staticmethod
    def generate_report(
        allocations: List[Allocation], 
        all_courses: List[Course], 
        all_classrooms: List[Classroom], 
        all_time_slots: List[TimeSlot],
        solver_result: Optional[SolverResult] = None,
        validation_result: Optional[ValidationResult] = None
    ) -> AnalyticsResult:
        
        report = AnalyticsResult()
        
        report.total_courses = len(all_courses)
        report.total_classrooms = len(all_classrooms)
        report.unallocated_courses = len(all_courses)
        report.allocated_courses = 0
        report.allocation_coverage_percentage = 0.0
        
        if not allocations:
            return report
            
        report.total_allocations = len(allocations)
        
        allocated_course_ids = set(a.course.id for a in allocations)
        report.allocated_courses = len(allocated_course_ids)
        
        if solver_result:
            report.unallocated_courses = len(solver_result.unallocated_courses)
        else:
            report.unallocated_courses = report.total_courses - report.allocated_courses
            
        if report.total_courses > 0:
            report.allocation_coverage_percentage = (report.allocated_courses / report.total_courses) * 100.0

        cr_usage = {cr.id: {"cr": cr, "sessions": 0, "wasted": 0} for cr in all_classrooms}
        fac_usage = {}
        ts_usage = {}
        day_usage = {}
        
        total_cap_eff = 0.0

        for a in allocations:
            cr = a.classroom
            ts = a.time_slot
            fac = a.faculty
            c = a.course
            
            hours = AnalyticsService._calculate_hours(ts.start_time, ts.end_time)
            report.total_teaching_hours += hours
            
            # Classroom stats
            cr_usage[cr.id]["sessions"] += 1
            cr_usage[cr.id]["wasted"] += max(0, cr.capacity - c.student_count)
            
            # Faculty stats
            if fac not in fac_usage:
                fac_usage[fac] = {"sessions": 0, "hours": 0.0}
            fac_usage[fac]["sessions"] += 1
            fac_usage[fac]["hours"] += hours
            
            # Time slot stats
            if ts.id not in ts_usage:
                ts_usage[ts.id] = {"day": ts.day.value, "time_str": f"{ts.start_time.strftime('%H:%M')} - {ts.end_time.strftime('%H:%M')}", "sessions": 0}
            ts_usage[ts.id]["sessions"] += 1
            
            # Day stats
            day = ts.day.value
            if day not in day_usage:
                day_usage[day] = {"sessions": 0, "hours": 0.0}
            day_usage[day]["sessions"] += 1
            day_usage[day]["hours"] += hours
            
            # Capacity efficiency using existing logic
            eff = Scoring.calc_capacity_efficiency(c.student_count, cr.capacity)
            total_cap_eff += eff

        report.average_capacity_efficiency = total_cap_eff / len(allocations)
        
        used_cr_count = 0
        for cr_id, data in cr_usage.items():
            cr = data["cr"]
            sessions = data["sessions"]
            available = len(cr.available_time_slots)
            util_pct = (sessions / available * 100.0) if available > 0 else 0.0
            
            if sessions > 0:
                used_cr_count += 1
                
            report.classroom_analytics.append(ClassroomAnalytics(
                classroom_id=cr.id,
                classroom_name=cr.name,
                room_type=cr.room_type.value,
                capacity=cr.capacity,
                allocated_sessions=sessions,
                available_sessions=available,
                utilization_percentage=util_pct,
                wasted_capacity=data["wasted"]
            ))
            
        # Sort classrooms by utilization
        report.classroom_analytics.sort(key=lambda x: x.allocated_sessions, reverse=True)
            
        report.used_classrooms = used_cr_count
        report.unused_classrooms = report.total_classrooms - used_cr_count

        for fac, data in fac_usage.items():
            report.faculty_analytics.append(FacultyAnalytics(
                faculty=fac,
                session_count=data["sessions"],
                total_teaching_hours=data["hours"]
            ))
        report.faculty_analytics.sort(key=lambda x: x.session_count, reverse=True)

        for ts_id, data in ts_usage.items():
            report.time_slot_analytics.append(TimeSlotAnalytics(
                time_slot_id=ts_id,
                day=data["day"],
                time_str=data["time_str"],
                allocated_sessions=data["sessions"]
            ))
        report.time_slot_analytics.sort(key=lambda x: x.allocated_sessions, reverse=True)
        
        for day, data in day_usage.items():
            report.day_analytics.append(DayAnalytics(
                day=day,
                allocated_sessions=data["sessions"],
                teaching_hours=data["hours"]
            ))
        report.day_analytics.sort(key=lambda x: x.allocated_sessions, reverse=True)

        if solver_result:
            report.overall_optimization_score = solver_result.score
            
        if validation_result:
            report.validation_status = validation_result.valid
            report.validation_violations_count = len(validation_result.violations)
            report.validation_passed_rules_count = len(validation_result.passed_rules)
            
        return report
