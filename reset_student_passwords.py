import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from users.models import User

students = User.objects.filter(role='student')
print(f"Resetting passwords for {students.count()} students...")

for s in students:
    s.set_password(s.username)
    s.must_change_password = True
    s.save()

print("All student passwords have been reset to their usernames.")
