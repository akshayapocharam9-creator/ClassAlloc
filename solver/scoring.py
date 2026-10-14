from typing import List, Dict, Tuple
from models import Allocation

from dataclasses import dataclass

@dataclass
class ScoringConfig:
    capacity_efficiency: float = 40.0
    time_preference: float = 20.0
    feature_efficiency: float = 20.0
    timetable_quality: float = 20.0

    @property
    def weights_dict(self) -> Dict[str, float]:
        return {
            "capacity_efficiency": self.capacity_efficiency,
            "time_preference": self.time_preference,
            "feature_efficiency": self.feature_efficiency,
            "timetable_quality": self.timetable_quality
        }

class Scoring:
    # Retained for backward compatibility if directly referenced, but evaluate() uses ScoringConfig
    WEIGHTS = {
        "capacity_efficiency": 40.0,
        "time_preference": 20.0,
        "feature_efficiency": 20.0,
        "timetable_quality": 20.0
    }

    @staticmethod
    def calc_capacity_efficiency(student_count: int, capacity: int) -> float:
        return (student_count / capacity) * 100.0

    @staticmethod
    def calc_time_preference(pref_list: List, assigned_ts_id: str) -> Tuple[float, str]:
        try:
            idx = [ts.id for ts in pref_list].index(assigned_ts_id)
            score = 100.0 - (idx * 20.0)
            return max(20.0, score), f"Assigned to preference #{idx + 1}"
        except ValueError:
            return 0.0, "Assigned time not in preferred list"

    @staticmethod
    def calc_feature_efficiency(req_len: int, avail_len: int) -> Tuple[float, str]:
        if avail_len == 0:
            return 100.0, "Room has no specialized features; perfect efficiency."
        raw_eff = (req_len / avail_len) * 100.0
        if req_len == 0:
            return 50.0, "Course requires 0 features but room is specialized (penalty applied)."
        return min(100.0, raw_eff), f"Course requires {req_len} features, room has {avail_len}."

    @staticmethod
    def calc_timetable_quality(times: List[object]) -> Tuple[float, int, str]:
        if len(times) <= 1:
            return 100.0, 0, "0 gaps > 2 hours"
        sorted_times = sorted(times)
        gaps = 0
        for i in range(1, len(sorted_times)):
            t1 = sorted_times[i-1]
            t2 = sorted_times[i]
            h_diff = (t2.hour * 60 + t2.minute) - (t1.hour * 60 + t1.minute)
            if h_diff > 120:
                gaps += 1
        
        if gaps == 0:
            score = 100.0
        elif gaps == 1:
            score = 70.0
        else:
            score = 40.0
            
        details = " | ".join([t.strftime('%H:%M') for t in sorted_times])
        return score, gaps, f"Gaps > 2h: {gaps}. Schedule: {details}"

    @staticmethod
    def evaluate(allocations: List[Allocation], config: ScoringConfig = None) -> Tuple[float, Dict[str, float]]:
        if config is None:
            config = ScoringConfig()
            
        if not allocations:
            return 0.0, {k: 0.0 for k in config.weights_dict.keys()}
            
        total_cap_eff = 0.0
        total_time_pref = 0.0
        total_feat_eff = 0.0
        
        faculty_schedule = {}
        
        for alloc in allocations:
            cap_eff = Scoring.calc_capacity_efficiency(alloc.course.student_count, alloc.classroom.capacity)
            total_cap_eff += cap_eff
            
            time_pref, _ = Scoring.calc_time_preference(alloc.course.preferred_time_slots, alloc.time_slot.id)
            total_time_pref += time_pref
            
            feat_eff, _ = Scoring.calc_feature_efficiency(len(alloc.course.required_features), len(alloc.classroom.features))
            total_feat_eff += feat_eff

            fac = alloc.faculty
            day = alloc.time_slot.day
            if fac not in faculty_schedule:
                faculty_schedule[fac] = {}
            if day not in faculty_schedule[fac]:
                faculty_schedule[fac][day] = []
            faculty_schedule[fac][day].append(alloc.time_slot.start_time)
            
        N = len(allocations)
        avg_cap_eff = total_cap_eff / N
        avg_time_pref = total_time_pref / N
        avg_feat_eff = total_feat_eff / N
        
        total_faculty_days = 0
        quality_score_sum = 0.0
        
        for fac, days in faculty_schedule.items():
            for day, times in days.items():
                total_faculty_days += 1
                score, _, _ = Scoring.calc_timetable_quality(times)
                quality_score_sum += score
                        
        avg_tt_quality = quality_score_sum / total_faculty_days if total_faculty_days > 0 else 100.0

        scores = {
            "capacity_efficiency": avg_cap_eff,
            "time_preference": avg_time_pref,
            "feature_efficiency": avg_feat_eff,
            "timetable_quality": avg_tt_quality
        }
        
        overall_score = 0.0
        for k, weight in config.weights_dict.items():
            overall_score += (scores[k] * (weight / 100.0))
            
        return overall_score, scores
