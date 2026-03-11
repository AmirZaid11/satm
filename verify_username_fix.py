import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from users.models import User
from django.core.exceptions import ValidationError

def test_slashed_username():
    print("Testing username validation with slashes...")
    test_username = 'CCS/00061/021'
    
    try:
        # Create a user object (don't save to DB yet to avoid potential cleanup issues)
        user = User(username=test_username, role='student')
        
        # Manually trigger Django's field validation
        user.full_clean()
        print(f"SUCCESS: Username '{test_username}' passed validation.")
        
    except ValidationError as e:
        print(f"FAILURE: Username '{test_username}' failed validation.")
        print(f"Errors: {e.message_dict}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_slashed_username()
