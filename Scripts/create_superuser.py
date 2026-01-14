import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital_ai.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "rihad")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "rihad@example.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "quantumsix")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created")
else:
    print("Superuser already exists")