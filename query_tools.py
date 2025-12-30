# backend/query_tools.py
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
faculty = pd.read_csv(os.path.join(DATA_DIR, "faculty_workload.csv"))
timetable = pd.read_csv(os.path.join(DATA_DIR, "timetable.csv"))

def get_faculty_workload(name):
    row = faculty[faculty["Name"].str.strip().str.lower() == name.strip().lower()]
    if row.empty:
        return f"Faculty '{name}' not found."
    hours = int(row["HoursPerWeek"].values[0])
    return f"{name} has {hours} hours of workload this week."

def faculty_free(day, time):
    booked = timetable[(timetable["Day"].str.strip().str.lower()==day.strip().lower()) &
                       (timetable["Time"].str.strip()==time.strip())]
    busy = booked["Faculty"].tolist()
    names = faculty["Name"].tolist()
    free = [n for n in names if n not in busy]
    if not busy:
        return f"No one is booked at {day} {time}. All faculty may be free.\nFree: {', '.join(free)}"
    return f"Busy at {day} {time}: {', '.join(busy)}\nFree: {', '.join(free)}"
