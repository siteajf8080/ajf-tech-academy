from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Lesson, Course  # Ajoute Lesson ak Course isit la

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
        labels = {
            'photo': 'Chwazi yon foto profil',
            'bio': 'Pale de ou menm',
            'telephone': 'Nimewo telefòn ou'
        }

# --- FÒM POU ENSTRIKTÈ AJOUTE LESON ---
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        # Ajiste field sa yo selon sa ki nan modèl Lesson ou a
        fields = ['course', 'title', 'content', 'video_url', 'order']
        
        labels = {
            'course': 'Chwazi Kou a',
            'title': 'Tit Leson an',
            'content': 'Kontni (Teks)',
            'video_url': 'Link Videyo (YouTube/Vimeo)',
            'order': 'Lòd leson sa a (Egz: 1, 2, 3...)'
        }
        
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Entwodiksyon sou Python'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Ekri kontni leson an isit la...'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    # Fonksyon sa a pèmèt enstriktè a wè SÈLMAN pwòp kou pa l yo nan dropdown an
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) # Nou pran itilizatè a nan view a
        super(LessonForm, self).__init__(*args, **kwargs)
        if user:
            # Sipoze modèl Course ou a gen yon field "instructor"
            self.fields['course'].queryset = Course.objects.filter(instructor=user)