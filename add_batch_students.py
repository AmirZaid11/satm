import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from users.models import User

def add_students(count=20, start_id=100):
    print(f"Adding {count} students starting from ID {start_id}...")
    
    created_count = 0
    for i in range(start_id, start_id + count):
        username = f"CCS/{i:05d}/025"
        
        if not User.objects.filter(username=username).exists():
            # Password and role details are handled by User.save()
            User.objects.create(
                username=username,
                role='student',
                first_name=f"Student",
                last_name=f"{i}"
            )
            created_count += 1
            print(f"Created: {username}")
        else:
            print(f"Skipped (exists): {username}")
            
    print(f"Successfully created {created_count} students.")

if __name__ == "__main__":
    add_students(20, 100)
