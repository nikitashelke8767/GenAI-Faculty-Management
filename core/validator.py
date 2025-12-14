from collections import defaultdict

def validate(entries, rules, meta):
    # Reconstruct Chronological Slots
    morning = rules["lecture_structure"]["morning"]
    afternoon = rules["lecture_structure"]["afternoon"]
    master_slots = morning + afternoon
    
    # Create a mapping: ("09:00", "10:00") -> Index 0
    slot_map = {tuple(slot): i for i, slot in enumerate(master_slots)}

    faculty_day_slots = defaultdict(list) # Changed to list to store indices

    for e in entries:
        if e.entry_type != "CLASS":
            continue

        # Look up the chronological index of this time slot
        time_key = (e.start_time, e.end_time)
        if time_key not in slot_map:
            # This handles Lab slots or weird times not in standard lecture slots
            continue

        idx = slot_map[time_key]
        key = (e.faculty_name, e.day)

        if idx in faculty_day_slots[key]:
             raise RuntimeError(f"Clash detected: {e.faculty_name} on {e.day} at {e.start_time}")
        
        faculty_day_slots[key].append(idx)

    # Validate Consecutive Rules
    if rules["policies"]["no_consecutive_lectures"] and not meta["allow_consecutive"]:
        for (faculty, day), slots in faculty_day_slots.items():
            slots.sort() # Must sort to check adjacency
            for i in range(len(slots) - 1):
                # If indices are exactly 1 apart, they are consecutive
                if slots[i+1] - slots[i] == 1:
                    # Optional: Check if there is a break between these indices
                    # e.g., if morning ends at index 1 and afternoon starts at index 2,
                    # and there is a lunch break, is that "consecutive"?
                    # For now, strict index checking implies consecutive.
                    raise RuntimeError(f"Consecutive violation: {faculty} on {day}")

    print("Validation Successful!")
    return True