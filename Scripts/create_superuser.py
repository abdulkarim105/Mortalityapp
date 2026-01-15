# Scripts/create_superuser.py
import os
import django


def main():
    # Ensure Django is configured
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital_ai.settings")
    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()

    username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "Quantumsix")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "rihad@example.com")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "datascience")

    # 1) Try exact username
    user = User.objects.filter(username=username).first()

    # 2) If not found, try any existing superuser and rename it
    if not user:
        user = User.objects.filter(is_superuser=True).first()
        if user and user.username != username:
            user.username = username
            print(f"Renaming existing superuser to '{username}'")

    if not user:
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser created")
        return

    # Update existing user
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    print("Superuser updated")


if __name__ == "__main__":
    main()
