from collections import defaultdict

def violates_consecutive(entries):
    faculty_map = defaultdict(list)

    for e in entries:
        if e.entry_type != "CLASS":
            continue
        faculty_map[e.faculty_name].append((e.day, e.start_time))

    for faculty, slots in faculty_map.items():
        slots.sort()
        for i in range(len(slots) - 1):
            if slots[i][0] == slots[i+1][0]:
                return True
    return False


def violates_daily_limit(entries, max_hours=4):
    daily_count = defaultdict(int)

    for e in entries:
        if e.entry_type != "CLASS":
            continue
        key = (e.faculty_name, e.day)
        daily_count[key] += 1
        if daily_count[key] > max_hours:
            return True
    return False
