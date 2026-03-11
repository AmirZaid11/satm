import re
import os

path = r'c:\Users\ANONYMOUS\Desktop\satm\templates\dashboards\lecturer.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Regular expression to find split Django template tags {{ ... }} and {% ... %}
# This will match tags that start with {{ or {% and end with }} or %} 
# potentially spanning multiple lines.
def join_tags(text):
    # Join {{ ... }} tags
    text = re.sub(r'\{\{\s*(.*?)\s*\}\}', lambda m: '{{ ' + m.group(1).replace('\n', ' ').replace('\r', '').strip() + ' }}', text, flags=re.DOTALL)
    # Join {% ... %} tags
    text = re.sub(r'\{%\s*(.*?)\s*%\}', lambda m: '{% ' + m.group(1).replace('\n', ' ').replace('\r', '').strip() + ' %}', text, flags=re.DOTALL)
    return text

new_content = join_tags(content)

if new_content != content:
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(new_content)
    print("SUCCESS: All split tags in lecturer.html joined.")
else:
    print("No split tags found or already joined.")
