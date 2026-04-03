from django.db import models
from django.contrib.auth.models import User

# --- PROFIL ITILIZATÈ ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Korije on_delete a la
    telephone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='profiles/', default='profiles/default.png')
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"Profil {self.user.username}"

# --- KOU YO ---
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='courses/', blank=True, null=True)

    def __str__(self):
        return self.title

# --- SISTÈM QUIZ ---
class Quiz(models.Model):
    # Nou chanje l an ForeignKey pou yon kou ka gen PLIZYÈ quiz (ex: Quiz 1, Quiz 2)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    pass_score = models.IntegerField(default=70)  # Pousantaj pou l pase (ex: 70%)

    def __str__(self):
        return f"{self.title} - {self.course.title}"

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

# --- REZILTA AK SÈTIFIKA ---
class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score}%)"

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    certificate_code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Sètifika {self.user.username} - {self.course.title}"