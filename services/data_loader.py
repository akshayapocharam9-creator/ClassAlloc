import json
from datetime import datetime
from typing import Dict, List, Tuple, Union

from models import DayOfWeek, RoomType, Feature, TimeSlot, Classroom, Course

class DataLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir

    def load_time_slots(self, file_name: str = "time_slots.json") -> Dict[str, TimeSlot]:
        with open(f"{self.data_dir}/{file_name}", "r") as f:
            data = json.load(f)
        
        time_slots = {}
        for item in data:
            ts_id = item["id"]
            day = DayOfWeek(item["day"])
            start = datetime.strptime(item["start_time"], "%H:%M").time()
            end = datetime.strptime(item["end_time"], "%H:%M").time()
            time_slots[ts_id] = TimeSlot(id=ts_id, day=day, start_time=start, end_time=end)
        return time_slots

    def load_classrooms(self, time_slots: Dict[str, TimeSlot], file_name: str = "classrooms.json") -> List[Classroom]:
        with open(f"{self.data_dir}/{file_name}", "r") as f:
            data = json.load(f)
        
        classrooms = []
        for item in data:
            room_type = RoomType(item["room_type"])
            features = {Feature(f) for f in item.get("features", [])}
            available_slots = []
            for ts_id in item.get("available_time_slots", []):
                if ts_id not in time_slots:
                    raise ValueError(f"Invalid time slot reference '{ts_id}' in classroom '{item['id']}'")
                available_slots.append(time_slots[ts_id])
                
            classrooms.append(
                Classroom(
                    id=item["id"],
                    name=item["name"],
                    building=item["building"],
                    capacity=item["capacity"],
                    room_type=room_type,
                    features=features,
                    available_time_slots=available_slots
                )
            )
        return classrooms

    def load_courses(self, time_slots: Dict[str, TimeSlot], file_name: str = "courses.json") -> List[Course]:
        with open(f"{self.data_dir}/{file_name}", "r") as f:
            data = json.load(f)
            
        courses = []
        for item in data:
            room_type = RoomType(item["required_room_type"])
            features = {Feature(f) for f in item.get("required_features", [])}
            preferred_slots = []
            for ts_id in item.get("preferred_time_slots", []):
                if ts_id not in time_slots:
                    raise ValueError(f"Invalid time slot reference '{ts_id}' in course '{item['id']}'")
                preferred_slots.append(time_slots[ts_id])
                
            courses.append(
                Course(
                    id=item["id"],
                    name=item["name"],
                    faculty=item["faculty"],
                    student_count=item["student_count"],
                    required_room_type=room_type,
                    required_features=features,
                    preferred_time_slots=preferred_slots,
                    section=item.get("section")
                )
            )
        return courses

    def load_all(self) -> Tuple[List[TimeSlot], List[Classroom], List[Course]]:
        time_slots_dict = self.load_time_slots()
        classrooms = self.load_classrooms(time_slots_dict)
        courses = self.load_courses(time_slots_dict)
        return list(time_slots_dict.values()), classrooms, courses

    def save_time_slots(self, time_slots: Union[List[TimeSlot], Dict[str, TimeSlot]], file_name: str = "time_slots.json") -> None:
        ts_list = time_slots.values() if isinstance(time_slots, dict) else time_slots
        data = []
        for ts in ts_list:
            data.append({
                "id": ts.id,
                "day": ts.day.value,
                "start_time": ts.start_time.strftime("%H:%M"),
                "end_time": ts.end_time.strftime("%H:%M")
            })
        with open(f"{self.data_dir}/{file_name}", "w") as f:
            json.dump(data, f, indent=4)

    def save_classrooms(self, classrooms: List[Classroom], file_name: str = "classrooms.json") -> None:
        data = []
        for cr in classrooms:
            data.append({
                "id": cr.id,
                "name": cr.name,
                "building": cr.building,
                "capacity": cr.capacity,
                "room_type": cr.room_type.value,
                "features": sorted([f.value for f in cr.features]),
                "available_time_slots": [ts.id for ts in cr.available_time_slots]
            })
        with open(f"{self.data_dir}/{file_name}", "w") as f:
            json.dump(data, f, indent=4)

    def save_courses(self, courses: List[Course], file_name: str = "courses.json") -> None:
        data = []
        for c in courses:
            data.append({
                "id": c.id,
                "name": c.name,
                "faculty": c.faculty,
                "student_count": c.student_count,
                "required_room_type": c.required_room_type.value,
                "required_features": sorted([f.value for f in c.required_features]),
                "preferred_time_slots": [ts.id for ts in c.preferred_time_slots],
                "section": c.section
            })
        with open(f"{self.data_dir}/{file_name}", "w") as f:
            json.dump(data, f, indent=4)

    def save_all(self, time_slots: Union[List[TimeSlot], Dict[str, TimeSlot]], classrooms: List[Classroom], courses: List[Course]) -> None:
        self.save_time_slots(time_slots)
        self.save_classrooms(classrooms)
        self.save_courses(courses)
