import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from django.contrib.auth.models import Group
from users.models import User

print("--- RBAC Verification ---")
print(f"Total Groups: {Group.objects.count()}")

for group in Group.objects.all():
    print(f"Group: {group.name} - Permissions: {group.permissions.count()} - Members: {group.user_set.count()}")

# Sample check
lecturer = User.objects.filter(role='lecturer').first()
if lecturer:
    print(f"Lecturer {lecturer.username} is in groups: {[g.name for g in lecturer.groups.all()]}")
    print(f"Lecturer is staff: {lecturer.is_staff}")

student = User.objects.filter(role='student').first()
if student:
    print(f"Student {student.username} is in groups: {[g.name for g in student.groups.all()]}")
    print(f"Student is staff: {student.is_staff}")
