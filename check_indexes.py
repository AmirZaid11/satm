import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

print("--- Indexes on timetabling_unit ---")
with connection.cursor() as cursor:
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='timetabling_unit';")
    rows = cursor.fetchall()
    for row in rows:
        print(f"Index: {row[0]}")
        print(f"SQL: {row[1]}")
        print("-" * 20)

if not rows:
    print("No indexes found on timetabling_unit.")
