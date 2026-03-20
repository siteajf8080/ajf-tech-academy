from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_one_delete=models.CASCADE)
    telephone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='profiles/', default='profiles/default.png')
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"Profil {self.user.username}"



from django.db import models
from .models import Course

class Quiz(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=255)
    pass_score = models.IntegerField(default=70)  # Pousantaj pou l pase (ex: 70%)

    def __str__(self):
        return f"Quiz: {self.course.title}"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text