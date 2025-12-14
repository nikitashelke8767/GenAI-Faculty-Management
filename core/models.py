from dataclasses import dataclass

@dataclass
class FacultyCourse:
    faculty_id: str
    faculty_name: str
    department: str
    course: str
    hours_per_week: int


@dataclass
class TimetableEntry:
    day: str
    start_time: str
    end_time: str
    entry_type: str   # CLASS / LAB / BREAK / GOLDEN_HOUR
    course: str
    faculty_name: str
