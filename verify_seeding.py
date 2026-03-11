import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from timetabling.models import Unit, Course
from django.db.models import Count

print("--- Data Verification ---")

# Check for duplicates by code, year, semester
duplicates = Unit.objects.values('code', 'year', 'semester').annotate(count=Count('id')).filter(count__gt=1)
if duplicates.exists():
    print(f"FAILED: Found {duplicates.count()} duplicate unit entries!")
    for d in duplicates:
        print(f"Duplicate: {d['code']} (Year {d['year']}, Sem {d['semester']}) - Count: {d['count']}")
else:
    print("SUCCESS: No duplicate units found by code/year/semester.")

# Check total counts
print(f"Total Unique Units: {Unit.objects.count()}")
print(f"Total Courses: {Course.objects.count()}")

# Verify specific shared units
shared_units = ["CIR 102", "PHT 112", "MAS 102", "MMA 102"]
for code in shared_units:
    unit = Unit.objects.filter(code=code).first()
    if unit:
        courses = list(unit.courses.values_list('name', flat=True))
        print(f"Unit {code} belongs to {len(courses)} courses: {', '.join(courses)}")
    else:
        print(f"Unit {code} not found!")

# Verify Year 4 visibility
y4_count = Unit.objects.filter(year=4).count()
print(f"Year 4 Units total: {y4_count}")
