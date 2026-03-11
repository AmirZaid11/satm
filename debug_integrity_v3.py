import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

def check_table(table_name):
    print(f"\n--- Checking table: {table_name} ---")
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"DESCRIBE {table_name}")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Error checking {table_name}: {e}")

from timetabling.models import Course

print("Attempting to create a Course via Django model...")
try:
    c = Course(name="Test Course Removal Debug")
    c.save()
    print("SUCCESS: Course saved via Django.")
    c.delete()
except Exception as e:
    print(f"FAILURE: Django save failed: {e}")
    import traceback
    traceback.print_exc()

check_table("timetabling_course")
check_table("timetabling_unit")

print("\n--- Listing all tables in satm_db ---")
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    for row in cursor.fetchall():
        print(row)
