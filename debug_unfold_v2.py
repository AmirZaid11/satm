import os
import sys
import traceback

# Add current directory to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')

print("--- SATM Diagnostic Script ---")
try:
    import django
    django.setup()
    print("SUCCESS: Django setup complete.")
except Exception:
    print("FAILURE: Django setup failed.")
    traceback.print_exc()
    sys.exit(1)

print("\nAttempting to import unfold.admin...")
try:
    import unfold.admin
    print("SUCCESS: unfold.admin imported successfully.")
except ImportError as e:
    print(f"FAILURE: ImportError in unfold.admin: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"FAILURE: Unexpected error in unfold.admin: {e}")
    traceback.print_exc()

print("\nChecking GenericStackedInline directly...")
try:
    from django.contrib.contenttypes.admin import GenericStackedInline
    print(f"SUCCESS: GenericStackedInline found: {GenericStackedInline}")
except ImportError as e:
    print(f"FAILURE: Could not import GenericStackedInline: {e}")
    traceback.print_exc()
