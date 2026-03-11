import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

with open('schema_output.txt', 'w') as f:
    f.write("--- Table Schema: timetabling_unit ---\n")
    with connection.cursor() as cursor:
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='timetabling_unit';")
        row = cursor.fetchone()
        f.write(row[0] if row else "Table not found!")
        f.write("\n\n--- Table Schema: timetabling_unit_courses ---\n")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='timetabling_unit_courses';")
        row = cursor.fetchone()
        f.write(row[0] if row else "Table not found!")
print("Schema written to schema_output.txt")
