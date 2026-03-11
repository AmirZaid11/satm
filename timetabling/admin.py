from django.contrib import admin
from .models import (
    Course, Unit, Room, TimeSlot, TimetableEntry,
    MissedClassReport, MakeupSlotRequest, LecturerAvailability
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'year', 'semester', 'lecturer')
    list_filter = ('year', 'semester')
    search_fields = ('code', 'name')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')
    search_fields = ('name',)

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time')
    list_filter = ('day',)

@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ('unit', 'room', 'time_slot')
    list_filter = ('time_slot__day', 'room')

@admin.register(MissedClassReport)
class MissedClassReportAdmin(admin.ModelAdmin):
    list_display = ('timetable_entry', 'date', 'status', 'reported_at')
    list_filter = ('status', 'date')

@admin.register(MakeupSlotRequest)
class MakeupSlotRequestAdmin(admin.ModelAdmin):
    list_display = ('get_unit_code', 'status', 'created_at')
    list_filter = ('status',)

    def get_unit_code(self, obj):
        return obj.missed_report.timetable_entry.unit.code
    get_unit_code.short_description = 'Unit Code'

@admin.register(LecturerAvailability)
class LecturerAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('lecturer', 'time_slot', 'is_available')
    list_filter = ('is_available', 'time_slot__day')
