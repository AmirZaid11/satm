import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("DESCRIBE timetabling_course")
    rows = cursor.fetchall()
    print("Columns in timetabling_course:")
    for row in rows:
        print(row)

    cursor.execute("DESCRIBE timetabling_unit")
    rows = cursor.fetchall()
    print("\nColumns in timetabling_unit:")
    for row in rows:
        print(row)
