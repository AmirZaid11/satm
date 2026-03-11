from django.db.models import Count, Sum, Q
from datetime import timedelta
from .models import TimetableEntry, Room, TimeSlot, Unit

def calculate_room_utilization():
    """
    Returns dict: {room_name: utilization_percentage}
    """
    total_slots = TimeSlot.objects.count()  # total possible slots per week
    if total_slots == 0:
        return {}

    utilization = {}
    for room in Room.objects.all():
        booked_slots = TimetableEntry.objects.filter(room=room).count()
        percentage = (booked_slots / total_slots) * 100 if total_slots > 0 else 0
        utilization[room.name] = round(percentage, 1)

    return utilization

def calculate_lecturer_workload():
    """
    Returns dict: {lecturer_username: total_hours, class_count}
    """
    workload = {}
    for entry in TimetableEntry.objects.select_related('unit__lecturer'):
        lecturer = entry.unit.lecturer
        if not lecturer:
            continue
        hours = (entry.time_slot.end_time.hour - entry.time_slot.start_time.hour) + \
                (entry.time_slot.end_time.minute - entry.time_slot.start_time.minute) / 60
        workload.setdefault(lecturer.username, {'hours': 0, 'classes': 0})
        workload[lecturer.username]['hours'] += hours
        workload[lecturer.username]['classes'] += 1

    return workload