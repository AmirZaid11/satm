import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from users.models import User
from django.contrib.auth import authenticate

def test_student_password_sync():
    print("Testing student username/password sync...")
    username = 'STUDENT/TEST/001'
    
    # Cleanup if exists
    User.objects.filter(username=username).delete()
    
    try:
        # Create student without password
        student = User.objects.create(username=username, role='student')
        print(f"Student created with role: {student.role}")
        
        # Verify authentication
        user = authenticate(username=username, password=username)
        if user:
            print(f"SUCCESS: Student '{username}' authenticated successfully with username as password.")
        else:
            print(f"FAILURE: Student '{username}' failed to authenticate with username as password.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        User.objects.filter(username=username).delete()

if __name__ == "__main__":
    test_student_password_sync()
