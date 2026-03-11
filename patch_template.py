"""
Directly patches student.html to fix all split Django template tags
in the makeup classes card section.
"""
import re

path = r'c:\Users\ANONYMOUS\Desktop\satm\templates\dashboards\student.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The entire broken makeup card (lines 194-214) - match loosely to handle line endings
OLD = (
    r'\{%\s*for makeup in makeup_classes\s*%\}.*?\{%\s*endfor\s*%\}'
)

NEW = """{% for makeup in makeup_classes %}
                    <div class="p-4 bg-red-950/20 border border-red-500/30 rounded-2xl hover:bg-red-900/30 transition-colors">
                        <div class="flex justify-between items-start mb-2">
                            <span class="px-2 py-0.5 bg-red-500/20 text-red-400 text-[10px] font-black tracking-wider uppercase rounded-md">{{ makeup.missed_report.timetable_entry.unit.code }}</span>
                            <span class="text-[10px] text-red-400 font-bold bg-red-500/10 px-2 py-0.5 rounded">{{ makeup.allocated_room.name }}</span>
                        </div>
                        <h3 class="text-sm font-bold text-white mb-2">{{ makeup.missed_report.timetable_entry.unit.name }}</h3>
                        <div class="flex items-center gap-2 text-xs text-gray-300">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            {{ makeup.allocated_date|date:"l, M d" }} at {{ makeup.allocated_time_slot.start_time|time:"H:i" }}
                        </div>
                    </div>
                    {% endfor %}"""

patched = re.sub(OLD, NEW, content, flags=re.DOTALL)

if patched == content:
    print("ERROR: Pattern not found - no changes made!")
    # Debug: show the offending section
    idx = content.find('for makeup in makeup_classes')
    print("Found loop at index:", idx)
    print(repr(content[idx:idx+600]))
else:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(patched)
    print("SUCCESS: Template patched!")
    # Verify
    idx = patched.find('for makeup in makeup_classes')
    print(patched[idx:idx+700])
