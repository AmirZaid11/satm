import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from users.models import User
from timetabling.models import TimetableEntry, Unit

students = []
for u in User.objects.filter(role='student'):
    c_id = u.course.id if u.course else None
    
    entries = []
    if c_id:
        qs = TimetableEntry.objects.filter(unit__courses=c_id, is_published=True, unit__year=u.year)
        entries = qs.count()

    students.append({
        'username': u.username,
        'course': u.course.name if u.course else None,
        'course_id': c_id,
        'year': u.year,
        'semester': u.semester,
        'entries_found': entries
    })

print(json.dumps(students, indent=2))
