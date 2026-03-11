from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from timetabling.models import TimetableEntry, Course, Unit
from .utils.generator import generate_master_timetable

@login_required
def generate_timetable_view(request):
    if request.user.role != 'admin':
        messages.error(request, "Access restricted to administrators only.")
        return redirect('login')
        
    success, msg = generate_master_timetable()
    if success:
        messages.success(request, msg)
        return redirect('master_timetable_view')
    else:
        messages.error(request, msg)
        return redirect('admin_dashboard')

@login_required
def publish_timetable_view(request):
    if request.user.role != 'admin':
        messages.error(request, "Access restricted to administrators only.")
        return redirect('login')
        
    updated = TimetableEntry.objects.filter(is_published=False).update(is_published=True)
    if updated > 0:
        messages.success(request, f"Successfully published the timetable. {updated} classes are now visible to students and lecturers.")
    else:
        messages.info(request, "No new classes to publish. The timetable is already fully shared.")
        
    return redirect('master_timetable_view')

@login_required
def master_timetable_view(request):
    if request.user.role != 'admin':
        messages.error(request, "Access restricted to administrators only.")
        return redirect('login')

    # Get all courses to determine groups
    try:
        ccs_course = Course.objects.get(name__icontains="Computer Science")
        cct_course = Course.objects.get(name__icontains="Computer Technology")
    except Course.DoesNotExist:
        ccs_course = None
        cct_course = None

    entries = TimetableEntry.objects.select_related('unit', 'room', 'time_slot').order_by('time_slot__day', 'time_slot__start_time')
    
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Get all unique start times from the database to form the columns
    all_time_objs = sorted(list(set(e.time_slot.start_time for e in entries)))
    from datetime import time
    if not all_time_objs:
        all_time_objs = [time(7,0), time(9,0), time(11,0), time(13,0), time(15,0), time(17,0)]

    # Define the standard groups we want to display as rows in order
    standard_groups = []
    for year in range(1, 5):
        standard_groups.append(f"CCS {year}")
        standard_groups.append(f"CCT {year}")

    # Initialize the deeply nested dictionary: Day -> Group -> Time -> Entry
    timetable_data = {day: {} for day in days_order}
    for day in days_order:
        for group in standard_groups:
            timetable_data[day][group] = {t: None for t in all_time_objs}

    for entry in entries:
        day = entry.time_slot.day
        t = entry.time_slot.start_time
        year = entry.unit.year
        courses = entry.unit.courses.all()
        
        applicable_groups = []
        if ccs_course and ccs_course in courses:
            applicable_groups.append(f"CCS {year}")
        if cct_course and cct_course in courses:
            applicable_groups.append(f"CCT {year}")
            
        for g in applicable_groups:
            if day in timetable_data and g in timetable_data[day]:
                timetable_data[day][g][t] = entry

    context = {
        'timetable_data': timetable_data,
        'all_times': all_time_objs,
    }
    return render(request, 'dashboards/master_timetable.html', context)