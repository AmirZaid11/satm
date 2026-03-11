from django.db import models
from users.models import User

class Course(models.Model):
    name = models.CharField(max_length=100)  # e.g. "Bachelor of Science in Computer Science"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Courses"


class Unit(models.Model):
    name = models.CharField(max_length=150)              # e.g. "Discrete Structures II"
    code = models.CharField(max_length=20)  # e.g. "CIR 102" – required for identification

    courses = models.ManyToManyField(Course, related_name='units')

    # Required academic context – now only on Unit
    year = models.PositiveSmallIntegerField(
        choices=[(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4')],
        default=1,
        help_text="Year in which this unit is taught"
    )
    semester = models.PositiveSmallIntegerField(
        choices=[(1, 'Semester 1'), (2, 'Semester 2')],
        default=1,
        help_text="Semester in which this unit is offered"
    )

    lecturer = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'lecturer'})
    duration_hours = models.PositiveIntegerField(default=2, help_text="Duration per session (hours)")
    students_count = models.PositiveIntegerField(default=50, help_text="Approximate number of students")

    class Meta:
        # unique_together = ('code', 'year', 'semester')  # Removed 'course' as M2M fields can't be here
        verbose_name_plural = "Units"

    def __str__(self):
        return f"{self.code} – {self.name} (Y{self.year}, Sem {self.semester})"

    def get_actual_students_count(self):
        """Dynamically calculates number of students based on User table."""
        from users.models import User
        count = User.objects.filter(
            role='student',
            course__in=self.courses.all(),
            year=self.year,
            semester=self.semester
        ).distinct().count()
        # If students are already registered for this group, use the real number.
        # This helps with room utilization (e.g. if only 10 students exist, don't reserve a 50-person hall).
        # Otherwise, fall back to the estimated/manual students_count.
        return count if count > 0 else self.students_count

class Room(models.Model):
    name = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} (Cap: {self.capacity})"

class TimeSlot(models.Model):
    day = models.CharField(max_length=10)  # Monday, Tuesday...
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('day', 'start_time')

    def __str__(self):
        return f"{self.day} {self.start_time} - {self.end_time}"


class TimetableEntry(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False, help_text="Set to True when the admin explicitly shares the timetable")

    class Meta:
        unique_together = ('room', 'time_slot')

    def __str__(self):
        return f"{self.unit.code} in {self.room.name} at {self.time_slot}"


class MissedClassReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('rescheduled', 'Rescheduled'),
    ]
    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE)
    date = models.DateField(help_text="The date of the missed class")
    reason = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            # Notify students
            from users.models import User
            unit = self.timetable_entry.unit
            students = User.objects.filter(
                role='student',
                course__in=unit.courses.all(),
                year=unit.year,
                semester=unit.semester
            )
            
            # 1. Notify Students (Student-friendly content, no reason)
            for student in students:
                Notification.objects.create(
                    recipient=student,
                    title=f"Class Cancellation: {unit.code}",
                    message=f"The class for {unit.name} on {self.date} has been report as missed/cancelled. A makeup session will be scheduled automatically soon.",
                    link=f"/dashboard/student/"
                )
            
            # 2. Notify Admins (Full details including reason)
            admins = User.objects.filter(role='admin')
            for admin in admins:
                Notification.objects.create(
                    recipient=admin,
                    title=f"Class Cancellation: {unit.code}",
                    message=f"Session for {unit.name} on {self.date} was missed due to: {self.reason}. The system is auto-scheduling a makeup.",
                    link=f"/dashboard/admin/"
                )


class MakeupSlotRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    missed_report = models.OneToOneField(MissedClassReport, on_delete=models.CASCADE, related_name='makeup_request')
    preferred_days = models.CharField(max_length=100, help_text="e.g. Monday, Wednesday")
    preferred_times = models.CharField(max_length=100, help_text="e.g. Morning, Afternoon", null=True, blank=True)
    duration_hours = models.PositiveIntegerField(default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    allocated_time_slot = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True)
    allocated_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    allocated_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_scheduled = False
        if self.pk:
            old_instance = MakeupSlotRequest.objects.get(pk=self.pk)
            if old_instance.status != 'scheduled' and self.status == 'scheduled':
                is_scheduled = True
        elif self.status == 'scheduled':
            is_scheduled = True
            
        super().save(*args, **kwargs)
        
        if is_scheduled:
            # Notify students
            from users.models import User
            unit = self.missed_report.timetable_entry.unit
            students = User.objects.filter(
                role='student',
                course__in=unit.courses.all(),
                year=unit.year,
                semester=unit.semester
            )
            
            for student in students:
                Notification.objects.create(
                    recipient=student,
                    title=f"Makeup Scheduled: {unit.code}",
                    message=f"Makeup class for {unit.name} on {self.allocated_date.strftime('%B %d')} at {self.allocated_time_slot.start_time.strftime('%H:%M')} in {self.allocated_room.name}.",
                    link=f"/dashboard/student/"
                )
                
            # Notify Admins
            admins = User.objects.filter(role='admin')
            for admin in admins:
                Notification.objects.create(
                    recipient=admin,
                    title=f"Makeup Automatically Scheduled",
                    message=f"A makeup class for {unit.code} was automatically scheduled for {self.allocated_date.strftime('%B %d')} at {self.allocated_time_slot.start_time.strftime('%H:%M')} in {self.allocated_room.name}.",
                    link=f"/dashboard/admin/"
                )

    def __str__(self):
        return f"Makeup for {self.missed_report.timetable_entry.unit.code}"


class LecturerAvailability(models.Model):
    lecturer = models.ForeignKey('users.User', on_delete=models.CASCADE, limit_choices_to={'role': 'lecturer'})
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('lecturer', 'time_slot')

    def __str__(self):
        status = "Available" if self.is_available else "Unavailable"
        return f"{self.lecturer.username} - {self.time_slot} ({status})"

class Notification(models.Model):
    recipient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: link to specific entities
    link = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"To {self.recipient.username}: {self.title}"

    class Meta:
        ordering = ['-created_at']
