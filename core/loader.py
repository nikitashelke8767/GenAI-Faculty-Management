import pandas as pd
from core.models import FacultyCourse

REQUIRED_COLUMNS = [
    "FacultyID", "Name", "Department", "Course", "HoursPerWeek"
]

def load_faculty_workload(path: str) -> list[FacultyCourse]:
    df = pd.read_csv(path)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    courses = []
    for _, row in df.iterrows():
        if row["HoursPerWeek"] <= 0:
            raise ValueError("HoursPerWeek must be positive")

        courses.append(
            FacultyCourse(
                faculty_id=row["FacultyID"],
                faculty_name=row["Name"],
                department=row["Department"],
                course=row["Course"],
                hours_per_week=int(row["HoursPerWeek"])
            )
        )

    return courses
