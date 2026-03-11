import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from users.models import User

def verify():
    test_cases = [
        # username, expected_course, expected_year
        ('CCS/00001/025', 'Computer Science', 1),
        ('CCT/00011/025', 'Computer Technology', 1),
        ('CCS/00021/024', 'Computer Science', 2),
        ('CCS/00022/023', 'Computer Science', 3),
        ('CCS/00023/022', 'Computer Science', 4),
        ('CCS/00061/021', 'Computer Science', 4),
    ]

    for username, exp_course, exp_year in test_cases:
        try:
            u = User.objects.get(username=username)
            course_ok = exp_course in u.course.name
            year_ok = u.year == exp_year
            pass_ok = u.check_password(username)
            print(f"[{username}] Course: {'OK' if course_ok else 'FAIL ' + u.course.name}, Year: {'OK' if year_ok else 'FAIL ' + str(u.year)}, Pass: {'OK' if pass_ok else 'FAIL'}")
        except User.DoesNotExist:
            print(f"[{username}] NOT FOUND")

if __name__ == '__main__':
    verify()
