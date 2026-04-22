import os
import django

# Ranplase 'config.settings' si katab settings ou a gen yon lòt non
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

username = 'SupperAJF-Tech'
email = 'jonathanfrancoisalcena08@gmail.com'
password = 'admin123' # Chanje sa si w vle

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("Superuser kreye ak siksè!")
else:
    print("Superuser sa a egziste deja.")