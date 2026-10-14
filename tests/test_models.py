import unittest
from datetime import time
from models import DayOfWeek, RoomType, Feature, TimeSlot, Classroom, Course, Allocation

class TestModels(unittest.TestCase):
    def test_time_slot_validation(self):
        with self.assertRaises(ValueError):
            TimeSlot("ts1", DayOfWeek.MONDAY, time(10, 0), time(9, 0))

    def test_classroom_validation(self):
        with self.assertRaises(ValueError):
            Classroom("cr1", "Room 101", "Main Building", 0, RoomType.LECTURE_HALL)

    def test_course_validation(self):
        with self.assertRaises(ValueError):
            Course("cs101", "Intro to CS", "Dr. Smith", -5, RoomType.COMPUTER_LAB)

    def test_allocation_validation(self):
        ts = TimeSlot("ts1", DayOfWeek.MONDAY, time(9, 0), time(10, 0))
        cr = Classroom("cr1", "Room 101", "Main", 30, RoomType.LECTURE_HALL, {Feature.PROJECTOR})
        c = Course("c1", "Math", "Dr. Jones", 40, RoomType.LECTURE_HALL) # 40 > 30 capacity

        with self.assertRaises(ValueError) as context:
            Allocation(c, cr, ts, "Dr. Jones")
        self.assertIn("capacity", str(context.exception).lower())

        c_wrong_type = Course("c2", "Chem", "Dr. A", 20, RoomType.SCIENCE_LAB)
        with self.assertRaises(ValueError) as context2:
            Allocation(c_wrong_type, cr, ts, "Dr. A")
        self.assertIn("match", str(context2.exception).lower())

if __name__ == '__main__':
    unittest.main()
