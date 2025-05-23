# delete_users.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoplift.settings")
django.setup()

from django.contrib.auth.models import User

# Exclude superuser if needed
# User.objects.exclude(is_superuser=True).delete()

User.objects.all().delete()
print("All users deleted.")
