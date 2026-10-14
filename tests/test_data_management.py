import unittest
import tempfile
import shutil
import datetime

from models import Course, Classroom, TimeSlot, RoomType, Feature, DayOfWeek
from services.data_loader import DataLoader

class TestDataManagementLogic(unittest.TestCase):
    def setUp(self):
        self.source_loader = DataLoader("data")
        self.ts, self.cr, self.c = self.source_loader.load_all()
        
        self.test_dir = tempfile.mkdtemp()
        self.dest_loader = DataLoader(self.test_dir)
        
        self.dest_loader.save_all(self.ts, self.cr, self.c)
        self.ts, self.cr, self.c = self.dest_loader.load_all()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_edit_course_logic(self):
        # Simulate the safe ID-based replacement logic used in the UI
        selected_id = self.c[0].id
        new_course = Course(
            id=selected_id,
            name="MODIFIED NAME",
            faculty=self.c[0].faculty,
            student_count=self.c[0].student_count,
            required_room_type=self.c[0].required_room_type,
            required_features=self.c[0].required_features,
            preferred_time_slots=self.c[0].preferred_time_slots,
            section=self.c[0].section
        )
        
        idx = next(i for i, c in enumerate(self.c) if c.id == selected_id)
        self.c[idx] = new_course
        
        self.dest_loader.save_courses(self.c)
        
        # Reload
        loaded_ts = self.dest_loader.load_time_slots()
        loaded_c = self.dest_loader.load_courses(loaded_ts)
        
        self.assertEqual(loaded_c[0].name, "MODIFIED NAME")


if __name__ == "__main__":
    unittest.main()
