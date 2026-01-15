# Scripts/create_superuser.py
import os
import sys

# 1) Add repo root to PYTHONPATH FIRST
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 2) Now Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital_ai.settings")

import django
django.setup()

from django.contrib.auth import get_user_model


def main():
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    if not username or not email or not password:
        raise RuntimeError("Missing DJANGO_SUPERUSER_USERNAME / EMAIL / PASSWORD env vars")

    User = get_user_model()

    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email},
    )

    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()

    print(f"✅ Superuser {'created' if created else 'updated'}: {username}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ create_superuser.py failed:", repr(e))
        sys.exit(1)
