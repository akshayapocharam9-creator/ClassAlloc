import unittest
import tempfile
import os
import shutil

from services.data_loader import DataLoader

class TestDataPersistence(unittest.TestCase):
    def setUp(self):
        # Read the real sample data from the existing data/ directory
        self.source_loader = DataLoader("data")
        self.ts, self.cr, self.c = self.source_loader.load_all()
        
        # Create a temp directory to safely write without modifying sample data
        self.test_dir = tempfile.mkdtemp()
        self.dest_loader = DataLoader(self.test_dir)
        
    def tearDown(self):
        # Safely remove the temp directory and files
        shutil.rmtree(self.test_dir)

    def test_save_and_load_time_slots(self):
        # Save original time slots to temp dir
        self.dest_loader.save_time_slots(self.ts)
        
        # Load them back
        loaded_ts = self.dest_loader.load_time_slots()
        self.assertEqual(len(loaded_ts), len(self.ts))
        
        # Verify equivalence
        for orig in self.ts:
            loaded = loaded_ts[orig.id]
            self.assertEqual(orig.day, loaded.day)
            self.assertEqual(orig.start_time, loaded.start_time)
            self.assertEqual(orig.end_time, loaded.end_time)

    def test_save_and_load_classrooms(self):
        # Classrooms require time_slots context
        self.dest_loader.save_time_slots(self.ts)
        self.dest_loader.save_classrooms(self.cr)
        
        loaded_ts = self.dest_loader.load_time_slots()
        loaded_cr = self.dest_loader.load_classrooms(loaded_ts)
        
        self.assertEqual(len(loaded_cr), len(self.cr))
        
        cr_dict = {cr.id: cr for cr in loaded_cr}
        for orig in self.cr:
            loaded = cr_dict[orig.id]
            self.assertEqual(orig.name, loaded.name)
            self.assertEqual(orig.capacity, loaded.capacity)
            self.assertEqual(orig.room_type, loaded.room_type)
            self.assertEqual(orig.features, loaded.features)
            self.assertEqual(
                [ts.id for ts in orig.available_time_slots],
                [ts.id for ts in loaded.available_time_slots]
            )

    def test_save_and_load_courses(self):
        self.dest_loader.save_time_slots(self.ts)
        self.dest_loader.save_courses(self.c)
        
        loaded_ts = self.dest_loader.load_time_slots()
        loaded_c = self.dest_loader.load_courses(loaded_ts)
        
        self.assertEqual(len(loaded_c), len(self.c))
        
        c_dict = {c.id: c for c in loaded_c}
        for orig in self.c:
            loaded = c_dict[orig.id]
            self.assertEqual(orig.name, loaded.name)
            self.assertEqual(orig.student_count, loaded.student_count)
            self.assertEqual(orig.required_room_type, loaded.required_room_type)
            self.assertEqual(orig.required_features, loaded.required_features)
            self.assertEqual(
                [ts.id for ts in orig.preferred_time_slots],
                [ts.id for ts in loaded.preferred_time_slots]
            )

if __name__ == "__main__":
    unittest.main()
