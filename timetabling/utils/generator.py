import hashlib
from ortools.sat.python import cp_model
from timetabling.models import Unit, Room, TimeSlot, TimetableEntry, Course
from users.models import User
from django.db import transaction

def get_state_hash():
    """Compute a hash of the current units, rooms, and active students/lecturers."""
    hash_str = ""
    # Units
    for u in Unit.objects.all().order_by('id'):
        # We include both the 'base' count and the 'registered' count in the hash
        # to ensure ANY student addition triggers a regeneration if it changes the registered count.
        registered_count = u.get_actual_students_count()
        hash_str += f"U{u.id}-base{u.students_count}-reg{registered_count}-{u.lecturer_id}-"
        for c in u.courses.all().order_by('id'):
            hash_str += f"C{c.id}-"
    # Rooms
    for r in Room.objects.all().order_by('id'):
        hash_str += f"R{r.id}-{r.capacity}-"
    # TimeSlots
    for ts in TimeSlot.objects.all().order_by('id'):
        hash_str += f"T{ts.id}-"
    
    return hashlib.md5(hash_str.encode('utf-8')).hexdigest()

def generate_master_timetable():
    """Generates the timetable utilizing Google OR-Tools. Returns (success, message)."""
    current_hash = get_state_hash()
    
    # We store the hash in a simple text file for idempotency
    hash_file_path = "last_timetable_hash.txt"
    try:
        with open(hash_file_path, "r") as f:
            last_hash = f.read().strip()
    except Exception:
        last_hash = ""

    if current_hash == last_hash and TimetableEntry.objects.exists():
        return True, "Timetable is already up-to-date. No changes detected."

    model = cp_model.CpModel()
    
    units = list(Unit.objects.all())
    rooms = list(Room.objects.all())
    timeslots = list(TimeSlot.objects.all())
    
    if not units or not rooms or not timeslots:
        return False, "Not enough data (units, rooms, or timeslots) to generate a timetable."

    # Cache actual students count for units
    unit_student_counts = {u.id: u.get_actual_students_count() for u in units}

    # Number of sessions per unit = 2 (for 4 hours total per week, since each slot is 2 hours)
    SESSIONS_PER_UNIT = 2

    x = {}
    for u in units:
        for s in range(SESSIONS_PER_UNIT):
            for r in rooms:
                for t in timeslots:
                    x[(u.id, s, r.id, t.id)] = model.NewBoolVar(f'x_{u.id}_{s}_{r.id}_{t.id}')

    # 1. EXACTLY ONE assignment per session per unit
    for u in units:
        for s in range(SESSIONS_PER_UNIT):
            model.AddExactlyOne(x[(u.id, s, r.id, t.id)] for r in rooms for t in timeslots)
            
    # 2. A unit cannot have both sessions at the *exact same time* (même timeslot)
    for u in units:
        for t in timeslots:
            model.AddAtMostOne(x[(u.id, s, r.id, t.id)] for s in range(SESSIONS_PER_UNIT) for r in rooms)

    # 3. Room capacity must be >= unit.students_count
    for u in units:
        actual_count = unit_student_counts[u.id]
        for s in range(SESSIONS_PER_UNIT):
            for r in rooms:
                if r.capacity < actual_count:
                    for t in timeslots:
                        model.Add(x[(u.id, s, r.id, t.id)] == 0)

    # 4. Room constraint: A room can host at most ONE session at any given time
    for r in rooms:
        for t in timeslots:
            model.AddAtMostOne(x[(u.id, s, r.id, t.id)] for u in units for s in range(SESSIONS_PER_UNIT))

    # 5. Lecturer constraint: A lecturer can teach at most ONE session at any given time
    lecturer_units = {}
    for u in units:
        if u.lecturer_id:
            if u.lecturer_id not in lecturer_units:
                lecturer_units[u.lecturer_id] = []
            lecturer_units[u.lecturer_id].append(u.id)

    for lect_id, l_units in lecturer_units.items():
        for t in timeslots:
            model.AddAtMostOne(
                x[(u_id, s, r.id, t.id)] 
                for u_id in l_units 
                for s in range(SESSIONS_PER_UNIT) 
                for r in rooms
            )

    # 6. Course+Year constraint
    course_year_units = {}
    for u in units:
        for c in u.courses.all():
            key = (c.id, u.year, u.semester)
            if key not in course_year_units:
                course_year_units[key] = []
            course_year_units[key].append(u.id)

    for key, c_units in course_year_units.items():
        for t in timeslots:
            model.AddAtMostOne(
                x[(u_id, s, r.id, t.id)] 
                for u_id in c_units 
                for s in range(SESSIONS_PER_UNIT) 
                for r in rooms
            )

    # 7. Optimization: Maximize room utilization by minimizing total capacity allocated
    # This encourages putting smaller classes in smaller rooms.
    model.Minimize(
        sum(x[(u.id, s, r.id, t.id)] * r.capacity 
            for u in units 
            for s in range(SESSIONS_PER_UNIT) 
            for r in rooms 
            for t in timeslots)
    )

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        # Save to DB
        with transaction.atomic():
            TimetableEntry.objects.all().delete()
            for u in units:
                for s in range(SESSIONS_PER_UNIT):
                    for r in rooms:
                        for t in timeslots:
                            if solver.Value(x[(u.id, s, r.id, t.id)]) == 1:
                                TimetableEntry.objects.create(
                                    unit=u,
                                    room=r,
                                    time_slot=t
                                )
        # Update hash
        with open(hash_file_path, "w") as f:
            f.write(current_hash)
            
        return True, "Timetable generated successfully!"
    else:
        return False, "Could not find a feasible schedule. Try adding more rooms or timeslots, or reducing constraints."
