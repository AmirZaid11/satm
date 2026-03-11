import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satm_core.settings')
django.setup()

User = get_user_model()
client = Client()

username = 'CCS/00001/025'
user = User.objects.get(username=username)
client.force_login(user)

response = client.get('/dashboard/student/', HTTP_HOST='127.0.0.1')
html = response.content.decode('utf-8')

with open('rendered.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Rendered HTML saved to rendered.html")
