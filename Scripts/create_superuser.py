from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "datascience")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "rihad@example.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "quantumsix")

# Try to find by username first
user = User.objects.filter(username=username).first()

# If not found, try to find old superuser and rename it
if not user:
    user = User.objects.filter(is_superuser=True).first()
    if user:
        user.username = username
        print(f"Renaming superuser to {username}")

if not user:
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    print("Superuser created")
else:
    user.email = email
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print("Superuser updated")