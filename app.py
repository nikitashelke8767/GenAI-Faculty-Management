import json
import os
import pandas as pd
from core.loader import load_faculty_workload
from core.generator import generate_timetable
from core.models import TimetableEntry 

def save_grid(timetable: list[TimetableEntry], filename: str = "data/timetable_output.csv"):
    # REVERTED to Standard 6 Slots
    time_slots = [
        "09:00-10:00", 
        "10:00-11:00", 
        "11:15-12:15", 
        "12:15-13:15", 
        "14:00-15:00", 
        "15:00-16:00"
    ]
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    grid_data = {day: {slot: [] for slot in time_slots} for day in days}

    for entry in timetable:
        text = f"{entry.course} ({entry.faculty_name})"
        
        slots_indices = []
        if entry.entry_type == "LAB":
            # Labs occupy 2 slots. We place the text in BOTH to show occupancy.
            if entry.start_time.startswith("09"): slots_indices = [0, 1]
            elif entry.start_time.startswith("11"): slots_indices = [2, 3]
            elif entry.start_time.startswith("14"): slots_indices = [4, 5]
        else:
            # Lectures occupy exactly 1 slot
            for i, slot_str in enumerate(time_slots):
                if entry.start_time == slot_str[:5]: 
                    slots_indices = [i]
                    break
        
        for idx in slots_indices:
            if idx < len(time_slots):
                slot_name = time_slots[idx]
                grid_data[entry.day][slot_name].append(text)

    # Flatten for CSV
    final_rows = []
    for day in days:
        row = {"Day": day}
        for slot in time_slots:
            items = grid_data[day][slot]
            if not items:
                row[slot] = ""
            else:
                # Sort alphabetically so parallel labs look neat
                items.sort()
                row[slot] = " || ".join(items)
        final_rows.append(row)

    df = pd.DataFrame(final_rows)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_csv(filename, index=False)
    print(f"\n✅ Timetable saved to {filename}")

if __name__ == "__main__":
    try:
        rules_path = "config/rules.json"
        if not os.path.exists(rules_path): rules_path = "rules.json"
        with open(rules_path, 'r') as f: rules = json.load(f)
        
        csv_path = "data/faculty_workload.csv"
        if not os.path.exists(csv_path): csv_path = "faculty_workload.csv"
        print(f"Loading {csv_path}...")
        courses = load_faculty_workload(csv_path)

        print("Generating Final Timetable...")
        timetable, _ = generate_timetable(courses, rules)

        save_grid(timetable)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")