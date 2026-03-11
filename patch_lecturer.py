"""
Directly patches lecturer.html to fix all split Django template tags.
"""
import re

path = r'c:\Users\ANONYMOUS\Desktop\satm\templates\dashboards\lecturer.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Timetable time range
content = re.sub(
    r'\{\{\s*entry\.time_slot\.start_time\|time:"H:i"\s*\}\}\s*-\s*\{\{\s*\n\s*entry\.time_slot\.end_time\|time:"H:i"\s*\}\}',
    '{{ entry.time_slot.start_time|time:"H:i" }} - {{ entry.time_slot.end_time|time:"H:i" }}',
    content, flags=re.MULTILINE
)

# Fix 2: Timetable room name
content = re.sub(
    r'rounded-md text-xs font-medium text-gray-300\"\}\}\{\s*\n\s*entry\.room\.name\s*\}\}',
    'rounded-md text-xs font-medium text-gray-300">{{ entry.room.name }}',
    content, flags=re.MULTILINE
)

# Fix 3: Sidebar unit code
content = re.sub(
    r'uppercase rounded-md\"\}\}\{\s*\n\s*unit\.code\s*\}\}',
    'uppercase rounded-md">{{ unit.code }}',
    content, flags=re.MULTILINE
)

# Fix 4: Sidebar course name
content = re.sub(
    r'bg-gray-800 text-gray-400 rounded-sm\"\}\}\{\s*\n\s*course\.name\s*\}\}',
    'bg-gray-800 text-gray-400 rounded-sm">{{ course.name }}',
    content, flags=re.MULTILINE
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Lecturer template patched!")
