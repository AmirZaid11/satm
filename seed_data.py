import os
import django
import random
from datetime import time

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from timetabling.models import Course, Unit, Room, TimeSlot, TimetableEntry

User = get_user_model()

def seed_data():
    print("Clearing old data...")
    # Delete in order to avoid FK constraint failures
    TimetableEntry.objects.all().delete()
    Unit.objects.all().delete()
    Course.objects.all().delete()
    Room.objects.all().delete()
    TimeSlot.objects.all().delete()
    User.objects.exclude(username='admin').delete()
    Group.objects.all().delete()

    print("Creating Groups and Permissions...")
    lecturer_group, _ = Group.objects.get_or_create(name="Lecturers")
    student_group, _ = Group.objects.get_or_create(name="Students")

    # Define permission codenames for groups
    lecturer_perms = [
        'view_unit', 'change_unit', 'view_timetableentry', 
        'view_room', 'view_timeslot', 'view_course'
    ]
    student_perms = [
        'view_unit', 'view_timetableentry', 'view_course'
    ]

    for codename in lecturer_perms:
        perm = Permission.objects.filter(codename=codename).first()
        if perm: lecturer_group.permissions.add(perm)
    
    for codename in student_perms:
        perm = Permission.objects.filter(codename=codename).first()
        if perm: student_group.permissions.add(perm)

    print("Seeding refined data with M2M support, Rooms, TimeSlots, and RBAC...")

    # 1. Create Courses
    cs_course = Course.objects.create(name="Bachelor of Science in Computer Science")
    ct_course = Course.objects.create(name="Bachelor of Science in Computer Technology")
    ph_course = Course.objects.create(name="Public Health")
    math_course = Course.objects.create(name="Mathematical Sciences")
    
    courses_map = {
        "CS": cs_course,
        "CT": ct_course,
        "PH": ph_course,
        "MATH": math_course
    }

    # 2. Seed Rooms
    rooms_data = [
        ("Computer Lab 1", 50),
        ("Computer Lab 2", 40),
        ("Lecture Hall A", 100),
        ("Lecture Hall B", 80),
        ("Room 101", 60),
        ("Room 102", 60),
    ]
    for name, cap in rooms_data:
        Room.objects.create(name=name, capacity=cap)
    print(f"Seeded {Room.objects.count()} rooms.")

    # 3. Seed TimeSlots (7am - 7pm, 2-hour blocks, Mon-Fri)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    start_hours = [7, 9, 11, 13, 15, 17] # 13=1pm, 15=3pm, 17=5pm
    for day in days:
        for hour in start_hours:
            TimeSlot.objects.create(
                day=day,
                start_time=time(hour, 0),
                end_time=time(hour + 2, 0)
            )
    print(f"Seeded {TimeSlot.objects.count()} time slots.")

    # 4. Helper to get/create lecturer
    lecturers_cache = {}
    def get_lecturer(name):
        if not name or name.strip() == "" or name.strip() == "All":
            return None
        
        username = name.lower().replace("dr. ", "").replace("mr. ", "").replace("ms. ", "").replace(" ", "").strip()
        if not username: return None
        
        if username in lecturers_cache:
            return lecturers_cache[username]
        
        display_name = name
        if username in ["smass", "sbe", "online", "all"]:
            display_name = name.upper() if len(name) <= 5 else name

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f"{username}@satm.com",
                'role': 'lecturer',
                'first_name': display_name,
                'is_staff': True # Allow login to admin
            }
        )
        if created:
            user.set_password("3639")
            user.save()
            # Add to Lecturer group
            lecturer_group = Group.objects.get(name="Lecturers")
            user.groups.add(lecturer_group)
        
        lecturers_cache[username] = user
        return user

    # Define all units once (Duration 2h per session, usually 2 sessions/week = 4h/week)
    all_units_data = [
        # Year 1 Sem 2
        (1, 2, "CIR 102", "Discrete Structures II", "SMASS", ["CS", "CT"]),
        (1, 2, "CIR 104", "Object Oriented programming I", "Dr. Obuhuma", ["CS", "CT"]),
        (1, 2, "CIR 106", "Database Systems", "Mr. Adongo", ["CS", "CT"]),
        (1, 2, "CIR 108", "Systems Analysis and Design", "Ms Vivian", ["CS"]),
        (1, 2, "CCS 122", "Electronics", "Dr. McOyowo", ["CS"]),
        (1, 2, "MAS 102", "Probability and Distribution Theory I", "SMASS", ["CS", "CT", "MATH"]),
        (1, 2, "MMA 102", "Calculus 1", "SMASS", ["CS", "MATH"]),
        (1, 2, "MMA 116", "Linear Algebra 1", "SMASS", ["CS", "MATH"]),
        (1, 2, "PHT 112", "HIV and AIDS Determinants prevention and management", "Online", ["CS", "CT", "PH"]),
        (1, 2, "CCT 102", "Engineering Mathematics II", "SMASS", ["CT", "MATH"]),
        (1, 2, "CCT 112", "Electronics II", "Mr. Konyino", ["CT"]),
        (1, 2, "CCT 116", "Digital Electronics I", "Mr. Nyabundi", ["CT"]),
        (1, 2, "CCT 118", "Digital Electronics I Lab", "Mr. Konyino", ["CT"]),
        
        # Year 2 Sem 2
        (2, 2, "CIR 204", "Object Oriented Analysis and Design", "Mr. Adongo", ["CS"]),
        (2, 2, "CIR 206", "Software Engineering", "Mr. Adongo", ["CS", "CT"]),
        (2, 2, "CIR 208", "Switching, Routing, and wireless Essentials", "Mr. Chamwama", ["CS", "CT"]),
        (2, 2, "CCS 210", "Automata Theory", "Dr. Obuhuma", ["CS", "CT"]),
        (2, 2, "CCT 210", "Data Communications", "Mr. Nyabundi", ["CS", "CT"]),
        (2, 2, "CCS 218", "Principles of Operating Systems", "Ms. Vivian", ["CS", "CT"]),
        (2, 2, "CCS 220", "Software Development Group Project", "Dr. Calvins", ["CS"]),
        (2, 2, "CCS 222", "Application Development for the Internet", "Dr. Obuhuma", ["CS"]),
        (2, 2, "CCT 202", "Digital Electronics II", "Dr. McOyowo", ["CT"]),
        (2, 2, "CCT 206", "Circuits and Systems", "Mr. Konyino", ["CT"]),
        (2, 2, "CCT 208", "Engineering Mathematics IV", "SMASS", ["CT", "MATH"]),

        # Year 3 Sem 2
        (3, 2, "CIR 302", "Human Computer Interaction", "Mr. Adongo", ["CS", "CT"]),
        (3, 2, "CIR 304", "Computer Graphics", "Mr. Bethuel", ["CS", "CT"]),
        (3, 2, "CIR 306", "Wireless and Mobile Computing", "Dr. McOyowo", ["CS", "CT"]),
        (3, 2, "CIR 308", "Database Administration", "Dr. Calvins", ["CS", "CT"]),
        (3, 2, "CIR 310", "Cryptography and Application", "Dr. Calvins", ["CS", "CT"]),
        (3, 2, "CIR 312", "Interconnecting Networks", "Mr. Chamwama", ["CS", "CT"]),
        (3, 2, "CCS 320", "Advanced Systems Development Project", "Mr. Adongo", ["CS"]),
        (3, 2, "CCS 322", "Evolutionary Computation", "", ["CS"]),
        (3, 2, "CCS 326", "Machine Learning", "Dr. Lilian", ["CS"]),
        (3, 2, "CCT 310", "Digital Control Systems", "", ["CT"]),
        (3, 2, "CCT 312", "Embedded Computing Systems I", "", ["CT"]),
        (3, 2, "CCT 314", "Digital Systems Design", "Mr. Konyino", ["CT"]),
        (3, 2, "CCT 316", "Digital Communications Systems", "Mr. Nyabundi", ["CT"]),
        (3, 2, "CCT 318", "Advanced Computer Architecture", "Mr. Nyabundi", ["CT"]),
        (3, 2, "CCT 324", "Advanced Computer Systems Design Project", "Dr. Calvins", ["CT"]),
        (3, 2, "CCT 303", "Digital Signal Processing", "Dr. McOyowo", ["CT"]),

        # Year 4 Sem 2
        (4, 2, "CCS 404", "Social Legal and ethical issues in Computing", "Ms Vivian", ["CS"]),
        (4, 2, "CCS 406", "Computer Science Project II", "All", ["CS"]),
        (4, 2, "CCS 412", "Natural Language Processing", "Dr. Lilian", ["CS"]),
        (4, 2, "CCS 414", "Pattern Recognition", "Ms. Vivian", ["CS"]),
        (4, 2, "CCS 416", "Information Retrieval", "Dr. Obuhuma", ["CS"]),
        (4, 2, "CCS 418", "Advanced Database Systems", "Mr. Adongo", ["CS"]),
        (4, 2, "CCS 422", "Advanced Compiler Construction and Design", "", ["CS"]),
        (4, 2, "BBE 411", "Entrepreneurship and Small Business Management", "SBE", ["CS", "CT"]),
        (4, 2, "CCT 402", "Computer-Aided Analysis and Design", "Mr. Nyabundi", ["CT"]),
        (4, 2, "CCT 406", "Computer Technology Project II", "All", ["CT"]),
        (4, 2, "CCT 407", "Social and Professional Issues", "Ms Vivian", ["CT"]),
        (4, 2, "CCT 412", "Computer Systems Engineering II", "Dr. McOyowo", ["CT"]),
        (4, 2, "CCT 418", "Natural Language Processing", "Dr. Lilian", ["CT"]),
        (4, 2, "CCT 420", "Pattern Recognition", "Ms. Vivian", ["CT"]),
        (4, 2, "CCT 424", "Advanced Database Systems", "Mr. Adongo", ["CT"]),
        (4, 2, "CCT 428", "Advanced Compiler Construction and Design", "", ["CT"]),
    ]

    for year, sem, code, name, lect, target_courses in all_units_data:
        lecturer = get_lecturer(lect)
        try:
            unit = Unit.objects.create(
                code=code, name=name, year=year, semester=sem,
                lecturer=lecturer, duration_hours=2,
                students_count=random.randint(40, 60)
            )
            for course_key in target_courses:
                unit.courses.add(courses_map[course_key])
            import sys; sys.stdout.flush()
        except Exception as e:
            import sys
            print(f"ERROR creating unit {code}: {e}")
            sys.stdout.flush()
            raise e

    print(f"Seeded {Unit.objects.count()} units across {Course.objects.count()} courses.")

    # 5. Create Students with admission-style usernames
    # CS Students
    for i in range(1, 11):
        username = f"CCS/{str(i).zfill(5)}/025"
        User.objects.create_user(
            username=username, email=f"student{i}@satm.com",
            role='student',
            first_name=f"CS Student", last_name=f"{i}"
        )
    
    # CT Students
    for i in range(11, 21):
        username = f"CCT/{str(i).zfill(5)}/025"
        User.objects.create_user(
            username=username, email=f"student{i}@satm.com",
            role='student',
            first_name=f"CT Student", last_name=f"{i}"
        )
    
    # Random older CS students for testing year assignment
    for i in range(21, 26):
        yr_suffix = f"02{5-(i-20)}" # 024, 023...
        username = f"CCS/{str(i).zfill(5)}/{yr_suffix}"
        User.objects.create_user(
            username=username, email=f"student{i}@satm.com",
            role='student',
            first_name=f"Senior Student", last_name=f"{i}"
        )

    print("Seeding complete with Many-to-Many association, Rooms, and TimeSlots!")


if __name__ == "__main__":
    seed_data()
