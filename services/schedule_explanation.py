from typing import List, Dict, Any
from dataclasses import dataclass, field
from models import Allocation
from solver.scoring import Scoring

@dataclass
class AllocationExplanation:
    course_id: str
    course_name: str
    faculty: str
    room_name: str
    time_str: str
    student_count: int
    capacity: int
    cap_eff: float
    time_pref_score: float
    feat_eff: float
    time_pref_details: str
    feat_details: str

@dataclass
class TimetableQualityExplanation:
    faculty: str
    day: str
    score: float
    gaps: int
    details: str

@dataclass
class ScheduleExplanation:
    allocations: List[AllocationExplanation] = field(default_factory=list)
    timetable_qualities: List[TimetableQualityExplanation] = field(default_factory=list)
    top_losses: List[Dict[str, Any]] = field(default_factory=list)

class ScheduleExplainer:
    @staticmethod
    def explain(allocations: List[Allocation]) -> ScheduleExplanation:
        expl = ScheduleExplanation()
        if not allocations:
            return expl

        faculty_schedule = {}

        for alloc in allocations:
            c = alloc.course
            cr = alloc.classroom
            ts = alloc.time_slot

            cap_eff = Scoring.calc_capacity_efficiency(c.student_count, cr.capacity)
            time_pref_score, time_pref_details = Scoring.calc_time_preference(c.preferred_time_slots, ts.id)
            feat_eff, feat_details = Scoring.calc_feature_efficiency(len(c.required_features), len(cr.features))

            a_expl = AllocationExplanation(
                course_id=c.id,
                course_name=c.name,
                faculty=alloc.faculty,
                room_name=cr.name,
                time_str=f"{ts.day.value} {ts.start_time.strftime('%H:%M')}",
                student_count=c.student_count,
                capacity=cr.capacity,
                cap_eff=cap_eff,
                time_pref_score=time_pref_score,
                feat_eff=feat_eff,
                time_pref_details=time_pref_details,
                feat_details=feat_details
            )
            expl.allocations.append(a_expl)

            fac = alloc.faculty
            day = ts.day.value
            if fac not in faculty_schedule:
                faculty_schedule[fac] = {}
            if day not in faculty_schedule[fac]:
                faculty_schedule[fac][day] = []
            faculty_schedule[fac][day].append(ts.start_time)

        for fac, days in faculty_schedule.items():
            for day, times in days.items():
                score, gaps, details = Scoring.calc_timetable_quality(times)
                expl.timetable_qualities.append(TimetableQualityExplanation(
                    faculty=fac, day=day, score=score, gaps=gaps, details=details
                ))

        losses = []
        for a in expl.allocations:
            c_loss = 100.0 - a.cap_eff
            t_loss = 100.0 - a.time_pref_score
            f_loss = 100.0 - a.feat_eff
            
            if c_loss > 0:
                losses.append({"category": "Capacity", "entity": f"{a.course_id} ({a.course_name})", "loss": c_loss, "desc": f"{a.student_count} students / {a.capacity} seats (Eff: {a.cap_eff:.1f}%)"})
            if t_loss > 0:
                losses.append({"category": "Time Preference", "entity": f"{a.course_id} ({a.course_name})", "loss": t_loss, "desc": a.time_pref_details})
            if f_loss > 0:
                losses.append({"category": "Feature Efficiency", "entity": f"{a.course_id} ({a.course_name})", "loss": f_loss, "desc": a.feat_details})

        for tq in expl.timetable_qualities:
            tq_loss = 100.0 - tq.score
            if tq_loss > 0:
                losses.append({"category": "Timetable Quality", "entity": f"{tq.faculty} / {tq.day}", "loss": tq_loss, "desc": tq.details})

        losses.sort(key=lambda x: x["loss"], reverse=True)
        expl.top_losses = losses[:15]

        return expl
