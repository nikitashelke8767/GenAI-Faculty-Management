import random
from collections import defaultdict
from core.models import TimetableEntry

# --- SLOT DEFINITIONS ---
MASTER_SLOTS = [
    ("09:00", "10:00"), 
    ("10:00", "11:00"), 
    ("11:15", "12:15"), 
    ("12:15", "13:15"), 
    ("14:00", "15:00"), 
    ("15:00", "16:00")  
]

def _get_daily_schedule():
    # Mon-Wed: Labs preferred 11:15-13:15
    MON_TUE_WED = {
        "VALID_SLOTS": [0, 1, 2, 3, 4, 5],
        "LAB_OPTIONS": [ {"time": ("11:15", "13:15"), "indices": [2, 3]} ]
    }
    
    # Thursday: Labs 09:00-11:00 OR 14:00-16:00
    THURSDAY = {
        "VALID_SLOTS": [0, 1, 2, 3, 4, 5],
        "LAB_OPTIONS": [
            {"time": ("09:00", "11:00"), "indices": [0, 1]},
            {"time": ("14:00", "16:00"), "indices": [4, 5]}
        ]
    }
    
    # Friday: Labs 14:00-16:00
    FRIDAY = {
        "VALID_SLOTS": [0, 1, 2, 3, 4, 5],
        "LAB_OPTIONS": [ {"time": ("14:00", "16:00"), "indices": [4, 5]} ]
    }
    
    # Saturday: ONLY 4 SLOTS (0, 1, 2, 3). No afternoon.
    SATURDAY = {
        "VALID_SLOTS": [0, 1, 2, 3], 
        "FIXED_LEC": (2, "GFM fixed lec", "PARUL RAJWADE"), # 11:15-12:15
        "LAB_OPTIONS": []
    }

    return {
        "Monday": MON_TUE_WED, "Tuesday": MON_TUE_WED, "Wednesday": MON_TUE_WED,
        "Thursday": THURSDAY, "Friday": FRIDAY, "Saturday": SATURDAY,
    }

def is_lab_course(course_name):
    # Standard Keywords
    keywords = ["lab", "laboratory", "practical", "workshop", "clinic", "project", "seminar"]
    # YOUR SPECIFIC SUBJECTS
    specific_labs = [
        "business communication", 
        "vocal science", 
        "value science", 
        "design thinking", 
        "innovation"
    ]
    
    name_lower = course_name.lower()
    
    if any(k in name_lower for k in keywords): return True
    if any(s in name_lower for s in specific_labs): return True
    return False

def generate_timetable(courses, rules):
    # Sort Labs first
    courses.sort(key=lambda x: (1 if is_lab_course(x.course) else 0, x.hours_per_week), reverse=True)
    try:
        return _generate_once(courses, rules)
    except Exception as e:
        print(f"Error: {e}")
        raise e

def _generate_once(courses, rules):
    timetable = []
    schedule = _get_daily_schedule()
    
    # --- TRACKERS ---
    faculty_busy = defaultdict(lambda: defaultdict(set))
    slot_state = defaultdict(lambda: defaultdict(lambda: None)) 
    lab_counts = defaultdict(lambda: defaultdict(int)) 
    
    faculty_daily_slots = defaultdict(lambda: defaultdict(set))
    daily_subjects = defaultdict(set)

    remaining_hours = {course.course: course.hours_per_week for course in courses}
    
    # ==========================================
    # STEP 1: PLACE FIXED GFM
    # ==========================================
    for day, cfg in schedule.items():
        if "FIXED_LEC" in cfg:
            idx, course_name, faculty_name = cfg["FIXED_LEC"]
            start, end = MASTER_SLOTS[idx]

            timetable.append(TimetableEntry(day, start, end, "CLASS", course_name, faculty_name))
            
            faculty_busy[faculty_name][day].add(idx)
            faculty_daily_slots[faculty_name][day].add(idx)
            slot_state[day][idx] = "LOCKED_LEC"
            
            if course_name in remaining_hours:
                remaining_hours[course_name] -= 1

    # ==========================================
    # STEP 2: PLACE LABS
    # ==========================================
    lab_pool = [c for c in courses if is_lab_course(c.course)]
    
    for day in rules["working_days"]:
        cfg = schedule[day]
        lab_options = cfg.get("LAB_OPTIONS", [])
        
        for opt in lab_options:
            indices = opt["indices"]
            start_t, end_t = opt["time"]
            
            # Skip if blocked
            if any(slot_state[day][i] == "LOCKED_LEC" for i in indices): continue
                
            # Try to fill 3 Batches
            for batch_num in range(3): 
                random.shuffle(lab_pool)
                
                for course in lab_pool:
                    if remaining_hours[course.course] <= 0: continue
                    
                    if any(i in faculty_busy[course.faculty_name][day] for i in indices): continue
                    
                    # Duplicate Check
                    current_labs = [e.course for e in timetable if e.day == day and e.entry_type == "LAB" and e.start_time == start_t[0]]
                    if course.course in current_labs: continue

                    # PLACE LAB
                    timetable.append(TimetableEntry(day, start_t[0], end_t[1], "LAB", course.course, course.faculty_name))
                    remaining_hours[course.course] -= 1
                    
                    for i in indices:
                        faculty_busy[course.faculty_name][day].add(i)
                        slot_state[day][i] = "LOCKED_LAB"
                        lab_counts[day][i] += 1
                        
                    break 

    # ==========================================
    # STEP 3: PLACE LECTURES
    # ==========================================
    lectures_pool = [c for c in courses if not is_lab_course(c.course)]
    
    for day in rules["working_days"]:
        valid_indices = schedule[day]["VALID_SLOTS"]
        
        for idx in valid_indices:
            if slot_state[day][idx] is not None: continue
            
            start, end = MASTER_SLOTS[idx]
            placed_slot = False
            
            random.shuffle(lectures_pool)
            
            for course in lectures_pool:
                if remaining_hours[course.course] <= 0: continue

                if idx in faculty_busy[course.faculty_name][day]: continue
                if (idx - 1) in faculty_daily_slots[course.faculty_name][day]: continue
                if (idx + 1) in faculty_daily_slots[course.faculty_name][day]: continue
                if course.course in daily_subjects[day]: continue

                # PLACE LECTURE
                timetable.append(TimetableEntry(day, start, end, "CLASS", course.course, course.faculty_name))
                remaining_hours[course.course] -= 1
                placed_slot = True
                
                faculty_busy[course.faculty_name][day].add(idx)
                faculty_daily_slots[course.faculty_name][day].add(idx)
                daily_subjects[day].add(course.course)
                slot_state[day][idx] = "LOCKED_LEC"
                break

    return timetable, {}