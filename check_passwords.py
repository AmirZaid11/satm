import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

from users.models import User

username = 'CCS/00001/022'
try:
    u = User.objects.get(username=username)
    is_correct = u.check_password(username)
    print(f"User: {u.username}, Password correct: {is_correct}")
except User.DoesNotExist:
    print(f"User {username} does not exist.")
