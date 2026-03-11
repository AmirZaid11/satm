import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')

try:
    import django
    django.setup()
    print("Django setup successful")
    
    print("Attempting to import unfold.admin...")
    import unfold.admin
    print("unfold.admin imported successfully")
except ImportError as e:
    print(f"ImportError: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
