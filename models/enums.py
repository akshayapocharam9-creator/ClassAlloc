from enum import Enum

class DayOfWeek(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

class RoomType(Enum):
    LECTURE_HALL = "Lecture Hall"
    SEMINAR_ROOM = "Seminar Room"
    COMPUTER_LAB = "Computer Lab"
    SCIENCE_LAB = "Science Lab"
    WORKSHOP = "Workshop"
    STUDIO = "Studio"

class Feature(Enum):
    PROJECTOR = "Projector"
    SMART_BOARD = "Smart Board"
    COMPUTERS = "Computers"
    WHITEBOARD = "Whiteboard"
    VIDEO_CONFERENCING = "Video Conferencing"
    ACCESSIBLE = "Accessible"
    LAB_EQUIPMENT = "Lab Equipment"
