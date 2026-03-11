import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from django.contrib.auth import authenticate
from users.models import User

def debug_auth():
    username = 'lecturer'
    password = 'lecturer@2026'
    
    print(f"--- Debugging Auth for {username} ---")
    
    # Check if user exists
    try:
        user_obj = User.objects.get(username=username)
        print(f"User found: {user_obj.username}")
        print(f"Role: {user_obj.role}")
        print(f"Is active: {user_obj.is_active}")
        print(f"Has usable password: {user_obj.has_usable_password()}")
        
        # Check password check directly
        is_pw_correct = user_obj.check_password(password)
        print(f"Direct password check (check_password): {is_pw_correct}")
        
    except User.DoesNotExist:
        print(f"User {username} does not exist!")
        return

    # Try full authenticate
    auth_user = authenticate(username=username, password=password)
    print(f"Result of authenticate(): {auth_user}")
    
    if auth_user is None:
        print("Reason for failure could be inactive user, or custom backend issues.")
        from django.conf import settings
        print(f"AUTHENTICATION_BACKENDS: {getattr(settings, 'AUTHENTICATION_BACKENDS', 'Default')}")

if __name__ == "__main__":
    debug_auth()
