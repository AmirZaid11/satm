import os
import django
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from users.models import User
from timetabling.models import Course

def generate_students(count=80):
    prefixes = ['CCS', 'CCT']
    suffixes = ['025', '024', '023', '022', '021'] # 021 will require manual year selection
    
    first_names = ["John", "Jane", "Samuel", "Mary", "David", "Alice", "Peter", "Lucy", "Michael", "Sarah", 
                   "Kevin", "Grace", "Paul", "Emma", "Robert", "Esther", "Daniel", "Joy", "Victor", "Faith"]
    last_names = ["Otieno", "Maina", "Kamau", "Ochieng", "Kibet", "Mulei", "Wanjiku", "Njoroge", "Muthoni", "Okello",
                  "Mwau", "Sanya", "Mbuvi", "Achieng", "Omondi", "Barasa", "Simiyu", "Were", "Oduor", "Ouma"]

    print(f"Generating {count} test students...")
    
    created_count = 0
    for i in range(count):
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        # ID number between 00001 and 00100
        id_num = str(random.randint(1, 100)).zfill(5)
        
        username = f"{prefix}/{id_num}/{suffix}"
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            continue
            
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='student'
        )
        # Note: save() will handle course and year auto-assignment
        created_count += 1

    print(f"Successfully created {created_count} students.")

if __name__ == "__main__":
    generate_students()
