import unittest
import json
import os
import shutil
from services.data_loader import DataLoader
from models import TimeSlot, Classroom, Course

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_data"
        os.makedirs(self.test_dir, exist_ok=True)
        
        self.ts_data = [
            {"id": "TS1", "day": "Monday", "start_time": "09:00", "end_time": "10:00"}
        ]
        self.cr_data = [
            {"id": "C1", "name": "Room 1", "building": "B1", "capacity": 30, "room_type": "Lecture Hall", "features": ["Projector"], "available_time_slots": ["TS1"]}
        ]
        self.c_data = [
            {"id": "CS1", "name": "Intro", "faculty": "Dr. X", "section": "A", "student_count": 20, "required_room_type": "Lecture Hall", "required_features": ["Projector"], "preferred_time_slots": ["TS1"]}
        ]
        
        with open(f"{self.test_dir}/time_slots.json", "w") as f:
            json.dump(self.ts_data, f)
        with open(f"{self.test_dir}/classrooms.json", "w") as f:
            json.dump(self.cr_data, f)
        with open(f"{self.test_dir}/courses.json", "w") as f:
            json.dump(self.c_data, f)
            
        self.loader = DataLoader(data_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_all_success(self):
        time_slots, classrooms, courses = self.loader.load_all()
        
        self.assertEqual(len(time_slots), 1)
        self.assertIsInstance(time_slots[0], TimeSlot)
        self.assertEqual(time_slots[0].id, "TS1")
        
        self.assertEqual(len(classrooms), 1)
        self.assertIsInstance(classrooms[0], Classroom)
        self.assertEqual(classrooms[0].id, "C1")
        self.assertEqual(len(classrooms[0].features), 1)
        
        self.assertEqual(len(courses), 1)
        self.assertIsInstance(courses[0], Course)
        self.assertEqual(courses[0].id, "CS1")
        
    def test_invalid_time_slot_reference(self):
        invalid_cr_data = [
            {"id": "C1", "name": "Room 1", "building": "B1", "capacity": 30, "room_type": "Lecture Hall", "features": [], "available_time_slots": ["INVALID_TS"]}
        ]
        with open(f"{self.test_dir}/classrooms.json", "w") as f:
            json.dump(invalid_cr_data, f)
            
        with self.assertRaisesRegex(ValueError, "Invalid time slot reference 'INVALID_TS'"):
            self.loader.load_all()

    def test_missing_data_files(self):
        os.remove(f"{self.test_dir}/time_slots.json")
        with self.assertRaises(FileNotFoundError):
            self.loader.load_all()

if __name__ == '__main__':
    unittest.main()
