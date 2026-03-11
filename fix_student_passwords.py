"""
Fix student passwords: sets each student's password to their username.
Uses direct set_password + save(update_fields=['password']) to bypass
the User.save() override which only sets passwords for NEW users.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from users.models import User

students = User.objects.filter(role='student')
total = students.count()
print(f"Found {total} student accounts. Resetting passwords...")

fixed = 0
already_ok = 0
failed = 0

for s in students:
    try:
        # Set password to username
        s.set_password(s.username)
        # Save ONLY the password field to avoid triggering other save() logic
        s.save(update_fields=['password'])
        
        # Verify it worked
        if s.check_password(s.username):
            fixed += 1
        else:
            print(f"  [VERIFY FAIL] {s.username}: password still does not match after reset")
            failed += 1
    except Exception as e:
        print(f"  [ERROR] {s.username}: {e}")
        failed += 1

print(f"\nDone! Fixed={fixed}, Failed={failed}, Total={total}")
print("\nVerification check on first 5 students:")
for s in User.objects.filter(role='student')[:5]:
    ok = s.check_password(s.username)
    print(f"  {s.username}: {'✓ OK' if ok else '✗ FAIL'}")
