import re
import os

files_to_fix = [
    r'c:\Users\ANONYMOUS\Desktop\satm\templates\dashboards\report_missed_class.html',
    r'c:\Users\ANONYMOUS\Desktop\satm\templates\dashboards\request_makeup_session.html',
    r'c:\Users\ANONYMOUS\Desktop\satm\templates\dashboards\set_availability.html'
]

def join_tags(text):
    # Join {{ ... }} tags
    text = re.sub(r'\{\{\s*(.*?)\s*\}\}', lambda m: '{{ ' + m.group(1).replace('\n', ' ').replace('\r', '').strip() + ' }}', text, flags=re.DOTALL)
    # Join {% ... %} tags
    text = re.sub(r'\{%\s*(.*?)\s*%\}', lambda m: '{% ' + m.group(1).replace('\n', ' ').replace('\r', '').strip() + ' %}', text, flags=re.DOTALL)
    return text

for path in files_to_fix:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = join_tags(content)
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
                f.write(new_content)
            print(f"SUCCESS: Split tags in {os.path.basename(path)} joined.")
        else:
            print(f"INFO: No split tags found in {os.path.basename(path)}.")
    else:
        print(f"ERROR: File not found: {path}")
