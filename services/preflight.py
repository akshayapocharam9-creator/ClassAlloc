from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from models import Course, Classroom, TimeSlot

@dataclass
class PreflightFinding:
    severity: str  # "CRITICAL", "WARNING", "HEALTHY"
    category: str
    entity: str
    message: str
    explanation: str
    suggested_action: str = ""

@dataclass
class CourseAnalysis:
    course_id: str
    domain_size: int
    severity: str
    issues: List[PreflightFinding] = field(default_factory=list)

@dataclass
class PreflightReport:
    overall_status: str
    total_courses: int
    total_classrooms: int
    total_time_slots: int
    critical_count: int = 0
    warning_count: int = 0
    healthy_count: int = 0
    findings: List[PreflightFinding] = field(default_factory=list)
    course_analysis: Dict[str, CourseAnalysis] = field(default_factory=dict)
    bottlenecks: List[PreflightFinding] = field(default_factory=list)

class PreflightIntelligence:
    def __init__(self, classrooms: List[Classroom], courses: List[Course], time_slots: List[TimeSlot]):
        self.classrooms = classrooms
        self.courses = courses
        self.time_slots = time_slots

    def analyze(self) -> PreflightReport:
        report = PreflightReport(
            overall_status="HEALTHY",
            total_courses=len(self.courses),
            total_classrooms=len(self.classrooms),
            total_time_slots=len(self.time_slots)
        )

        faculty_time_slots = {}
        for c in self.courses:
            if c.faculty not in faculty_time_slots:
                faculty_time_slots[c.faculty] = []
            faculty_time_slots[c.faculty].append(c)
            
            c_analysis = CourseAnalysis(course_id=c.id, domain_size=0, severity="HEALTHY")
            
            compatible_rooms = []
            for cr in self.classrooms:
                if cr.room_type == c.required_room_type and c.required_features.issubset(cr.features):
                    compatible_rooms.append(cr)
            
            if not compatible_rooms:
                finding = PreflightFinding(
                    severity="CRITICAL",
                    category="Room Compatibility",
                    entity=c.name,
                    message=f"No compatible rooms found.",
                    explanation=f"Requires {c.required_room_type.value} and features {', '.join([f.value for f in c.required_features])}.",
                    suggested_action="Add a classroom matching these requirements or reduce course requirements."
                )
                c_analysis.issues.append(finding)
                report.findings.append(finding)
            else:
                if len(compatible_rooms) == 1 and c.required_features:
                    finding = PreflightFinding(
                        severity="WARNING",
                        category="Resource Constraint",
                        entity=c.name,
                        message=f"Only 1 compatible room exists for required features.",
                        explanation=f"Room {compatible_rooms[0].name} is the only room with the required features.",
                        suggested_action="Consider adding features to other rooms to prevent bottlenecks."
                    )
                    c_analysis.issues.append(finding)
                    report.findings.append(finding)
                    
                max_cap = max(cr.capacity for cr in compatible_rooms)
                if c.student_count > max_cap:
                    finding = PreflightFinding(
                        severity="CRITICAL",
                        category="Capacity Feasibility",
                        entity=c.name,
                        message=f"No compatible classroom can accommodate {c.student_count} students.",
                        explanation=f"Largest compatible classroom capacity: {max_cap}. Required: {c.student_count}.",
                        suggested_action="Add a larger classroom or reduce the section size."
                    )
                    c_analysis.issues.append(finding)
                    report.findings.append(finding)
                else:
                    valid_rooms = [cr for cr in compatible_rooms if cr.capacity >= c.student_count]
                    domain_size = 0
                    possible_ts = c.preferred_time_slots if c.preferred_time_slots else self.time_slots
                    
                    for r in valid_rooms:
                        for ts in possible_ts:
                            if ts in r.available_time_slots:
                                domain_size += 1
                                
                    c_analysis.domain_size = domain_size
                    
                    if domain_size == 0:
                        finding = PreflightFinding(
                            severity="CRITICAL",
                            category="Time-Slot Feasibility",
                            entity=c.name,
                            message="Zero scheduling possibilities.",
                            explanation="No combination of compatible room and valid time slot exists.",
                            suggested_action="Expand preferred time slots or increase room availability."
                        )
                        c_analysis.issues.append(finding)
                        report.findings.append(finding)
                    elif domain_size == 1:
                        finding = PreflightFinding(
                            severity="CRITICAL",
                            category="Domain Size",
                            entity=c.name,
                            message="Only 1 valid scheduling possibility.",
                            explanation="Highly constrained. Any conflict will make this course impossible.",
                            suggested_action="Add more preferred time slots or compatible rooms."
                        )
                        c_analysis.issues.append(finding)
                        report.findings.append(finding)
                    elif domain_size <= 3:
                        finding = PreflightFinding(
                            severity="WARNING",
                            category="Domain Size",
                            entity=c.name,
                            message=f"Only {domain_size} valid scheduling possibilities.",
                            explanation="Highly constrained course.",
                            suggested_action="Consider expanding options."
                        )
                        c_analysis.issues.append(finding)
                        report.findings.append(finding)
                        
            report.course_analysis[c.id] = c_analysis

        for fac, courses in faculty_time_slots.items():
            if len(courses) > len(self.time_slots):
                finding = PreflightFinding(
                    severity="CRITICAL",
                    category="Faculty Workload",
                    entity=fac,
                    message=f"Assigned to {len(courses)} courses but only {len(self.time_slots)} time slots exist.",
                    explanation="Mathematically impossible to schedule all courses without double-booking.",
                    suggested_action="Reassign some courses to another faculty member."
                )
                report.findings.append(finding)
                
            strict_courses = [c for c in courses if len(c.preferred_time_slots) == 1]
            ts_counts = {}
            for c in strict_courses:
                ts = c.preferred_time_slots[0]
                ts_counts[ts.id] = ts_counts.get(ts.id, 0) + 1
                if ts_counts[ts.id] > 1:
                    finding = PreflightFinding(
                        severity="CRITICAL",
                        category="Faculty Time Conflict",
                        entity=fac,
                        message=f"Multiple courses strictly require the same time slot.",
                        explanation=f"Course {c.name} strictly requires {ts.day.value} {ts.start_time.strftime('%H:%M')}, which conflicts with another assignment.",
                        suggested_action="Change preferred time slots for these courses."
                    )
                    report.findings.append(finding)
                    
        feature_counts = {}
        for cr in self.classrooms:
            for f in cr.features:
                feature_counts[f] = feature_counts.get(f, 0) + 1
                
        for f, count in feature_counts.items():
            if count == 1:
                courses_needing_f = [c for c in self.courses if f in c.required_features]
                if len(courses_needing_f) > 3:
                    finding = PreflightFinding(
                        severity="WARNING",
                        category="Resource Bottleneck",
                        entity=f.value,
                        message=f"Feature {f.value} exists in only 1 room, but {len(courses_needing_f)} courses require it.",
                        explanation="This creates a severe scheduling bottleneck.",
                        suggested_action="Add this feature to more classrooms."
                    )
                    report.bottlenecks.append(finding)
                    report.findings.append(finding)
                    
        report.critical_count = len([f for f in report.findings if f.severity == "CRITICAL"])
        report.warning_count = len([f for f in report.findings if f.severity == "WARNING"])
        report.healthy_count = len([c for c in report.course_analysis.values() if not c.issues])
        
        if report.critical_count > 0:
            report.overall_status = "CRITICAL"
        elif report.warning_count > 0:
            report.overall_status = "WARNING"
            
        return report
