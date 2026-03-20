from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

# --- FÒM POU KREYE KONT (SIGNUP) ---
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Mete yon imel ki valid.")

    class Meta:
        model = User
        fields = ("username", "email")


# --- FÒM POU MODIFIE DONE UTILIZATÈ (USER) ---
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']


# --- FÒM POU MODIFIE PROFIL (FOTO, BIO, TEL) ---
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'telephone']
        # Nou ka ajoute bèl label an kreyòl si n vle
        labels = {
            'photo': 'Chwazi yon foto profil',
            'bio': 'Pale de ou menm',
            'telephone': 'Nimewo telefòn ou'
        }