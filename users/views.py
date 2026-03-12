from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from timetabling.models import TimetableEntry, MissedClassReport, MakeupSlotRequest, LecturerAvailability, TimeSlot

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from .forms import StudentProfileForm
import tablib

def login_view(request):
    # Allow authenticated users to see the login page if they explicitly navigate there,
    # satisfying the user's request to "always take me to login page".
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            messages.success(request, f"Welcome, {user.get_full_name() or user.username}!")
            
            # Respect 'next' parameter if present, but only if it matches role
            next_url = request.GET.get('next')
            if next_url:
                # Basic role-based prefix check for safety
                is_valid_next = True
                if user.role == 'student' and 'lecturer' in next_url:
                    is_valid_next = False
                elif user.role == 'lecturer' and 'student' in next_url:
                    is_valid_next = False
                
                if is_valid_next:
                    return redirect(next_url)
                
            return redirect_based_on_role(request, user)
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'login.html')

@login_required
def force_password_change(request):
    # Keeping the view active in case users manually visit it, but it's optional
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            
            user.must_change_password = False
            user.save()
            
            messages.success(request, 'Your password was successfully updated!')
            return redirect_based_on_role(request, user)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
        
    template_name = 'users/force_password_change.html'
    if request.user.role == 'lecturer':
        template_name = 'dashboards/change_password.html'
    elif request.user.role == 'student':
        # If students have a custom one, add here. For now, keep default
        pass
        
    return render(request, template_name, {'form': form})

def redirect_based_on_role(request, user):
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'lecturer':
        return redirect('lecturer_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
    else:
        messages.error(request, "No valid role assigned to this account.")
        return redirect('login')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


# Placeholder dashboards – we'll style them next
@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.warning(request, "Access restricted to administrators only.")
        return redirect('login')
        
    from timetabling.models import Course, Unit, Room, TimetableEntry, MakeupSlotRequest, Notification
    
    context = {
        'user': request.user,
        'courses_count': Course.objects.count(),
        'units_count': Unit.objects.count(),
        'rooms_count': Room.objects.count(),
        'published_count': TimetableEntry.objects.filter(is_published=True).count(),
        'recent_makeups': MakeupSlotRequest.objects.all().select_related('missed_report__timetable_entry__unit', 'allocated_room', 'allocated_time_slot').order_by('-created_at')[:5],
        'notifications': Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5],
    }
    return render(request, 'dashboards/admin.html', context)

@login_required
def lecturer_dashboard(request):
    if request.user.role != 'lecturer':
        messages.error(request, "Access restricted to lecturers only.")
        return redirect('login')

    # Get filter parameters
    year_filter = request.GET.get('year')
    semester_filter = request.GET.get('semester')

    # Get lecturer's timetable entries (Show ALL assigned, not just published, for the lecturer to see their schedule)
    raw_entries = TimetableEntry.objects.filter(
        unit__lecturer=request.user
    ).select_related('unit', 'room', 'time_slot').order_by('time_slot__day', 'time_slot__start_time')
    
    # Get units assigned to this lecturer
    from timetabling.models import Unit
    assigned_units = Unit.objects.filter(lecturer=request.user).prefetch_related('courses')

    # Apply filters to assigned_units (for the "Your Units" sidebar)
    if year_filter and year_filter.isdigit():
        assigned_units = assigned_units.filter(year=int(year_filter))
    if semester_filter and semester_filter.isdigit():
        assigned_units = assigned_units.filter(semester=int(semester_filter))

    # Structure data for the HTML Grid (Day -> Time -> Entry)
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    all_time_objs = sorted(list(set(e.time_slot.start_time for e in raw_entries)))
    
    from datetime import time
    if not all_time_objs:
        all_time_objs = [time(7,0), time(9,0), time(11,0), time(13,0), time(15,0), time(17,0)]

    timetable_data = {day: {t: None for t in all_time_objs} for day in days_order}
    
    for entry in raw_entries:
        day = entry.time_slot.day
        t = entry.time_slot.start_time
        if day in timetable_data:
            timetable_data[day][t] = entry

    # Get recent missed class reports
    missed_reports = MissedClassReport.objects.filter(timetable_entry__unit__lecturer=request.user).order_by('-reported_at')[:5]

    # Get scheduled makeup classes
    from timetabling.models import MakeupSlotRequest
    from django.utils import timezone
    makeup_classes = MakeupSlotRequest.objects.filter(
        status='scheduled',
        missed_report__timetable_entry__unit__lecturer=request.user,
        allocated_date__gte=timezone.now().date()
    ).select_related('missed_report__timetable_entry__unit', 'allocated_time_slot', 'allocated_room').order_by('allocated_date', 'allocated_time_slot__start_time')

    context = {
        'timetable_data': timetable_data,
        'all_times': all_time_objs,
        'entries': raw_entries,  # Add this for stats.count
        'assigned_units': assigned_units,
        'missed_reports': missed_reports,
        'makeup_classes': makeup_classes,
        'user': request.user,
        'current_year': year_filter,
        'current_semester': semester_filter,
    }
    return render(request, 'dashboards/lecturer.html', context)

@login_required
def report_missed_class(request):
    if request.user.role != 'lecturer':
        return redirect('login')

    if request.method == 'POST':
        entry_id = request.POST.get('timetable_entry')
        date = request.POST.get('date')
        reason = request.POST.get('reason')
        preferred_days = request.POST.getlist('preferred_days')
        
        try:
            entry = TimetableEntry.objects.get(id=entry_id, unit__lecturer=request.user)
        except TimetableEntry.DoesNotExist:
            messages.error(request, "The selected timetable session no longer exists. It may have been updated or regenerated.")
            return redirect('lecturer_dashboard')

        report = MissedClassReport.objects.create(
            timetable_entry=entry,
            date=date,
            reason=reason
        )
        
        # Auto-schedule logic
        from timetabling.models import TimeSlot, Room, MakeupSlotRequest
        import datetime
        from django.utils import timezone
        
        days_to_check = preferred_days + [d for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] if d not in preferred_days]
        assigned_slot = None
        assigned_room = None
        
        course_ids = entry.unit.courses.values_list('id', flat=True)
        year = entry.unit.year
        
        for day in days_to_check:
            if assigned_slot: break
            slots = TimeSlot.objects.filter(day=day).order_by('start_time')
            for slot in slots:
                if assigned_slot: break
                
                # Lecturer check
                lec_tt = TimetableEntry.objects.filter(unit__lecturer=request.user, time_slot=slot, is_published=True).exists()
                lec_mu = MakeupSlotRequest.objects.filter(missed_report__timetable_entry__unit__lecturer=request.user, allocated_time_slot=slot, status='scheduled').exists()
                if lec_tt or lec_mu: continue
                
                # Student check
                stu_tt = TimetableEntry.objects.filter(unit__courses__in=course_ids, unit__year=year, time_slot=slot, is_published=True).exists()
                stu_mu = MakeupSlotRequest.objects.filter(missed_report__timetable_entry__unit__courses__in=course_ids, missed_report__timetable_entry__unit__year=year, allocated_time_slot=slot, status='scheduled').exists()
                if stu_tt or stu_mu: continue
                
                # Room check
                for room in Room.objects.all():
                    rm_tt = TimetableEntry.objects.filter(room=room, time_slot=slot, is_published=True).exists()
                    rm_mu = MakeupSlotRequest.objects.filter(allocated_room=room, allocated_time_slot=slot, status='scheduled').exists()
                    if not rm_tt and not rm_mu:
                        assigned_slot = slot
                        assigned_room = room
                        break

        if assigned_slot:
            today = timezone.localtime().date()
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            target_idx = days_of_week.index(assigned_slot.day)
            curr_idx = today.weekday()
            days_ahead = target_idx - curr_idx
            if days_ahead <= 0: days_ahead += 7
            next_date = today + datetime.timedelta(days=days_ahead)
            
            MakeupSlotRequest.objects.create(
                missed_report=report,
                preferred_days=", ".join(preferred_days),
                status='scheduled',
                allocated_time_slot=assigned_slot,
                allocated_room=assigned_room,
                allocated_date=next_date
            )
            messages.success(request, f"Makeup scheduled successfully! Found slot on {next_date.strftime('%A, %b %d')} at {assigned_slot.start_time.strftime('%H:%M')} in {assigned_room.name}.")
        else:
            MakeupSlotRequest.objects.create(
                missed_report=report,
                preferred_days=", ".join(preferred_days),
                status='pending'
            )
            messages.warning(request, "Reported, but the system could not find a clash-free slot. Flagged for manual review.")
            
        return redirect('lecturer_dashboard')

    entries = TimetableEntry.objects.filter(unit__lecturer=request.user).select_related('unit', 'time_slot')
    return render(request, 'dashboards/report_missed_class.html', {'entries': entries})

@login_required
def set_availability(request):
    if request.user.role != 'lecturer':
        return redirect('login')

    if request.method == 'POST':
        # Clear existing and set new
        LecturerAvailability.objects.filter(lecturer=request.user).delete()
        
        slot_ids = request.POST.getlist('slots')
        for slot_id in slot_ids:
            try:
                slot = TimeSlot.objects.get(id=slot_id)
                LecturerAvailability.objects.create(
                    lecturer=request.user,
                    time_slot=slot,
                    is_available=True
                )
            except TimeSlot.DoesNotExist:
                continue # Skip invalid slots
        messages.success(request, "Availability updated.")
        return redirect('lecturer_dashboard')

    all_slots = TimeSlot.objects.all().order_by('day', 'start_time')
    current_availability = LecturerAvailability.objects.filter(lecturer=request.user, is_available=True).values_list('time_slot_id', flat=True)
    
    return render(request, 'dashboards/set_availability.html', {
        'all_slots': all_slots,
        'current_availability': list(current_availability)
    })

@login_required
def request_makeup_session(request, report_id):
    if request.user.role != 'lecturer':
        return redirect('login')
        
    try:
        report = MissedClassReport.objects.get(id=report_id, timetable_entry__unit__lecturer=request.user)
    except MissedClassReport.DoesNotExist:
        messages.error(request, "The missed class report you are looking for does not exist.")
        return redirect('lecturer_dashboard')
    
    if request.method == 'POST':
        preferred_days = request.POST.get('preferred_days')
        preferred_times = request.POST.get('preferred_times')
        duration = request.POST.get('duration_hours')
        
        MakeupSlotRequest.objects.create(
            missed_report=report,
            preferred_days=preferred_days,
            preferred_times=preferred_times,
            duration_hours=duration
        )
        messages.success(request, "Makeup session request submitted successfully.")
        return redirect('lecturer_dashboard')
        
    return render(request, 'dashboards/request_makeup_session.html', {'report': report})


@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        messages.warning(request, "Access restricted to students only.")
        return redirect('login')
        
    # Force profile update if year is not set
    if not request.user.year:
        messages.info(request, "Please set your current year of study to continue.")
        return redirect('student_profile_update')

    view_type = request.GET.get('view', 'individual') # 'individual' or 'department'
    entries = []
    
    active_year = request.GET.get('year', str(request.user.year) if request.user.year else '1')
    active_sem = request.GET.get('semester', str(request.user.semester) if request.user.semester else '1')
    
    if request.user.course:
        queryset = TimetableEntry.objects.filter(unit__courses=request.user.course, is_published=True)
        
        # In 'individual' view, filter by the student's current year/semester
        if view_type == 'individual':
            queryset = queryset.filter(unit__year=active_year, unit__semester=active_sem)
        else:
            # Department view: allow explicit filtering
            if request.GET.get('year'):
                queryset = queryset.filter(unit__year=request.GET.get('year'))
            if request.GET.get('semester'):
                queryset = queryset.filter(unit__semester=request.GET.get('semester'))
        
        raw_entries = queryset.select_related('unit', 'room', 'time_slot').distinct().order_by('time_slot__day', 'time_slot__start_time')
    else:
        raw_entries = TimetableEntry.objects.none()

    # 1. Structure data for the HTML Grid (Day -> Time -> Entry)
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    all_time_objs = sorted(list(set(e.time_slot.start_time for e in raw_entries)))
    
    from datetime import time
    if not all_time_objs:
        all_time_objs = [time(7,0), time(9,0), time(11,0), time(13,0), time(15,0), time(17,0)]

    timetable_data = {day: {t: None for t in all_time_objs} for day in days_order}
    
    for entry in raw_entries:
        day = entry.time_slot.day
        t = entry.time_slot.start_time
        if day in timetable_data:
            timetable_data[day][t] = entry

    # 2. Advanced Next Class Calculation
    from django.utils import timezone
    import datetime
    
    # Use localtime to respect the TIME_ZONE setting (Africa/Nairobi) instead of pure UTC
    now = timezone.localtime()
    current_day = now.strftime('%A')
    current_time = now.time()
    
    next_class = None
    class_state = 'empty' # 'ongoing', 'next', 'future', 'empty'
    class_day_name = ''
    
    # Check for classes happening today that haven't ended yet
    today_classes = raw_entries.filter(time_slot__day=current_day, time_slot__end_time__gt=current_time).order_by('time_slot__start_time')
    
    if today_classes.exists():
        next_class = today_classes.first()
        if next_class.time_slot.start_time <= current_time:
            class_state = 'ongoing'
        else:
            class_state = 'next'
    else:
        # Check for classes on future days
        day_indices = {d: i for i, d in enumerate(days_order)}
        current_idx = day_indices.get(current_day, -1)
        
        future_class = None
        
        # Check remaining days in the week
        for i in range(current_idx + 1, len(days_order)):
            day_name = days_order[i]
            day_classes = raw_entries.filter(time_slot__day=day_name).order_by('time_slot__start_time')
            if day_classes.exists():
                future_class = day_classes.first()
                break
                
        # If no classes later this week, check from Monday
        if not future_class:
            for i in range(0, current_idx + 1):
                day_name = days_order[i]
                day_classes = raw_entries.filter(time_slot__day=day_name).order_by('time_slot__start_time')
                if day_classes.exists():
                    future_class = day_classes.first()
                    break
        
        if future_class:
            next_class = future_class
            class_state = 'future'
            class_day_name = future_class.time_slot.day

    # Calculate Greeting
    hour = now.hour
    if hour < 12:
        greeting = "Morning"
    elif hour < 17:
        greeting = "Afternoon"
    else:
        greeting = "Evening"

    # Calculate Academic Progress (Mock for now, based on units completed/enrolled)
    # In a real system, you'd check grades or attendance
    academic_progress = 75 # Standardized progress
    academic_progress_offset = (academic_progress / 100) * 175.9

    # Fetch Notifications
    from timetabling.models import MissedClassReport, MakeupSlotRequest
    notifications = []
    
    # Fetch Makeup Classes for this student
    makeup_classes = MakeupSlotRequest.objects.none()
    if request.user.course:
        makeup_classes = MakeupSlotRequest.objects.filter(
            status='scheduled',
            missed_report__timetable_entry__unit__courses=request.user.course,
            missed_report__timetable_entry__unit__year=active_year,
            allocated_date__gte=timezone.now().date()
        ).select_related('missed_report__timetable_entry__unit', 'allocated_time_slot', 'allocated_room').order_by('allocated_date', 'allocated_time_slot__start_time')
    # Fetch Notifications for the student
    from timetabling.models import Notification
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]

    context = {
        'greeting': greeting,
        'next_class': next_class,
        'class_state': class_state,
        'class_day_name': class_day_name,
        'timetable_data': timetable_data,
        'all_times': all_time_objs,
        'active_year': active_year,
        'active_semester': active_sem,
        'notifications': notifications,
        'makeup_classes': makeup_classes,
    }
    
    return render(request, 'dashboards/student.html', context)

@login_required
def student_profile_update(request):
    if request.user.role != 'student':
        return redirect('login')
        
    profile_form = StudentProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = StudentProfileForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Your academic profile has been updated.")
                return redirect('student_dashboard')
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your security key has been updated successfully.")
                return redirect('student_dashboard')
            else:
                messages.error(request, "Please correct the errors in the security form.")

    return render(request, 'dashboards/student_profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })

@login_required
def export_timetable(request):
    if request.user.role != 'student' or not request.user.course:
        return redirect('student_dashboard')
        
    queryset = TimetableEntry.objects.filter(
        unit__courses=request.user.course,
        is_published=True
    )
    
    # Respect active filters during export
    year_filter = request.GET.get('year')
    sem_filter = request.GET.get('semester')
    
    if year_filter:
        queryset = queryset.filter(unit__year=year_filter)
    if sem_filter:
        queryset = queryset.filter(unit__semester=sem_filter)
        
    entries = queryset.select_related('unit', 'room', 'time_slot').order_by('time_slot__day', 'time_slot__start_time')
    
    dataset = tablib.Dataset()
    dataset.headers = ['Unit Code', 'Unit Name', 'Day', 'Start Time', 'End Time', 'Room']
    
    for entry in entries:
        dataset.append([
            entry.unit.code,
            entry.unit.name,
            entry.time_slot.day,
            entry.time_slot.start_time.strftime('%H:%M'),
            entry.time_slot.end_time.strftime('%H:%M'),
            entry.room.name
        ])
    
    export_format = request.GET.get('format', 'csv')
    
    if export_format == 'excel':
        content = dataset.xlsx
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        extension = 'xlsx'
    else:
        content = dataset.csv
        content_type = 'text/csv'
        extension = 'csv'
        
    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="timetable.{extension}"'
    return response
@login_required
def delete_notification(request, notification_id):
    from timetabling.models import Notification
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.delete()
    return JsonResponse({'status': 'success'})
