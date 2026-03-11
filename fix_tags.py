import os

file_path = r"c:\Users\ANONYMOUS\Desktop\satm\templates\dashboards\student.html"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i].rstrip('\n')
    
    # Check for open tag {{ or {% without closing tag on same line
    open_tag = None
    if "{{" in line and "}}" not in line:
        open_tag = ("{{", "}}")
    elif "{%" in line and "%}" not in line:
        open_tag = ("{%", "%}")
        
    if open_tag:
        start, end = open_tag
        merged = line
        j = i + 1
        found_end = False
        while j < len(lines) and j < i + 10: # search up to 10 lines ahead
            next_line = lines[j].strip()
            merged += " " + next_line
            if end in next_line:
                found_end = True
                break
            j += 1
            
        if found_end:
            # Clean up double spaces
            merged = ' '.join(merged.split())
            new_lines.append(merged)
            i = j + 1
            continue
            
    new_lines.append(line)
    i += 1

with open(file_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("Student dashboard tags unified line-by-line.")
