import json
import os

os.makedirs('data', exist_ok=True)

time_slots = []
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
times = [
    ("09:00", "10:00"),
    ("10:00", "11:00"),
    ("11:15", "12:15"),
    ("12:15", "13:15"),
    ("14:00", "15:00"),
    ("15:00", "16:00"),
    ("16:00", "17:00")
]
for day in days:
    for start, end in times:
        ts_id = f"TS_{day[:3].upper()}_{start.replace(':', '')}"
        time_slots.append({
            "id": ts_id,
            "day": day,
            "start_time": start,
            "end_time": end
        })

with open('data/time_slots.json', 'w') as f:
    json.dump(time_slots, f, indent=2)

classrooms = [
    {"id": "CR_101", "name": "Alan Turing Hall", "building": "CS Building", "capacity": 150, "room_type": "Lecture Hall", "features": ["Projector", "Smart Board", "Accessible"], "available_time_slots": [ts["id"] for ts in time_slots]},
    {"id": "CR_102", "name": "Ada Lovelace Lab", "building": "CS Building", "capacity": 40, "room_type": "Computer Lab", "features": ["Computers", "Projector"], "available_time_slots": [ts["id"] for ts in time_slots]},
    {"id": "CR_103", "name": "Seminar Room A", "building": "CS Building", "capacity": 20, "room_type": "Seminar Room", "features": ["Whiteboard", "Video Conferencing"], "available_time_slots": [ts["id"] for ts in time_slots]},
    {"id": "CR_104", "name": "Workshop 1", "building": "Engineering Block", "capacity": 30, "room_type": "Workshop", "features": ["Lab Equipment", "Whiteboard"], "available_time_slots": [ts["id"] for ts in time_slots]},
    {"id": "CR_201", "name": "Physics Lab", "building": "Science Block", "capacity": 35, "room_type": "Science Lab", "features": ["Lab Equipment"], "available_time_slots": [ts["id"] for ts in time_slots]},
    {"id": "CR_202", "name": "Chemistry Lab", "building": "Science Block", "capacity": 35, "room_type": "Science Lab", "features": ["Lab Equipment", "Accessible"], "available_time_slots": [ts["id"] for ts in time_slots]},
    {"id": "CR_301", "name": "Lecture Room B", "building": "Main Block", "capacity": 80, "room_type": "Lecture Hall", "features": ["Projector", "Whiteboard"], "available_time_slots": [ts["id"] for ts in time_slots]},
    {"id": "CR_302", "name": "Lecture Room C", "building": "Main Block", "capacity": 60, "room_type": "Lecture Hall", "features": ["Projector", "Smart Board"], "available_time_slots": [ts["id"] for ts in time_slots]},
    {"id": "CR_303", "name": "Studio X", "building": "Arts Block", "capacity": 25, "room_type": "Studio", "features": ["Whiteboard"], "available_time_slots": [ts["id"] for ts in time_slots]},
    {"id": "CR_401", "name": "AI Research Lab", "building": "CS Building", "capacity": 20, "room_type": "Computer Lab", "features": ["Computers", "Projector", "Smart Board"], "available_time_slots": [ts["id"] for ts in time_slots]}
]
with open('data/classrooms.json', 'w') as f:
    json.dump(classrooms, f, indent=2)

courses = [
    {"id": "CS101-A", "name": "Intro to Programming", "faculty": "Dr. Smith", "section": "A", "student_count": 35, "required_room_type": "Computer Lab", "required_features": ["Computers", "Projector"], "preferred_time_slots": ["TS_MON_0900", "TS_WED_0900"]},
    {"id": "CS101-B", "name": "Intro to Programming", "faculty": "Dr. Smith", "section": "B", "student_count": 35, "required_room_type": "Computer Lab", "required_features": ["Computers", "Projector"], "preferred_time_slots": ["TS_TUE_0900", "TS_THU_0900"]},
    {"id": "CS201-A", "name": "Data Structures", "faculty": "Prof. Johnson", "section": "A", "student_count": 120, "required_room_type": "Lecture Hall", "required_features": ["Projector", "Smart Board"], "preferred_time_slots": ["TS_MON_1000", "TS_WED_1000"]},
    {"id": "CS305-A", "name": "Artificial Intelligence", "faculty": "Dr. Lee", "section": "A", "student_count": 60, "required_room_type": "Lecture Hall", "required_features": ["Projector"], "preferred_time_slots": ["TS_TUE_1115", "TS_THU_1115"]},
    {"id": "CS305-LAB", "name": "AI Lab", "faculty": "Dr. Lee", "section": "A", "student_count": 20, "required_room_type": "Computer Lab", "required_features": ["Computers", "Smart Board"], "preferred_time_slots": ["TS_FRI_1400"]},
    {"id": "DS401-A", "name": "Big Data Analytics", "faculty": "Dr. Chen", "section": "A", "student_count": 45, "required_room_type": "Lecture Hall", "required_features": ["Projector"], "preferred_time_slots": ["TS_MON_1400", "TS_WED_1400"]},
    {"id": "PHY101-A", "name": "Physics I", "faculty": "Dr. Miller", "section": "A", "student_count": 75, "required_room_type": "Lecture Hall", "required_features": ["Projector", "Whiteboard"], "preferred_time_slots": ["TS_TUE_1400", "TS_THU_1400"]},
    {"id": "PHY101-LAB", "name": "Physics I Lab", "faculty": "Dr. Miller", "section": "A", "student_count": 30, "required_room_type": "Science Lab", "required_features": ["Lab Equipment"], "preferred_time_slots": ["TS_WED_1500"]},
    {"id": "ENG101-A", "name": "Engineering Workshop", "faculty": "Mr. Davis", "section": "A", "student_count": 25, "required_room_type": "Workshop", "required_features": ["Lab Equipment"], "preferred_time_slots": ["TS_FRI_0900", "TS_FRI_1000"]},
    {"id": "MTH201-A", "name": "Linear Algebra", "faculty": "Dr. White", "section": "A", "student_count": 55, "required_room_type": "Lecture Hall", "required_features": ["Whiteboard"], "preferred_time_slots": ["TS_MON_1115", "TS_WED_1115", "TS_FRI_1115"]},
    {"id": "SEM400-A", "name": "Senior Seminar", "faculty": "Prof. Black", "section": "A", "student_count": 15, "required_room_type": "Seminar Room", "required_features": ["Video Conferencing"], "preferred_time_slots": ["TS_THU_1500", "TS_THU_1600"]}
]
with open('data/courses.json', 'w') as f:
    json.dump(courses, f, indent=2)

print(f"Created {len(time_slots)} time slots, {len(classrooms)} classrooms, {len(courses)} courses.")
