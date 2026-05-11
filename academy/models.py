from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from datetime import timedelta

# ======================================================
# --- 1. MODÃˆL POU KOU YO ---
# ======================================================
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Pri kou a an HTG")
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='courses_taught')

    def __str__(self):
        return self.title

# ======================================================
# --- 2. MODÃˆL POU LESON YO (MIZAJOU) ---
# ======================================================
class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True, help_text="Deskripsyon oswa kontni tÃ¨ks leson an")
    video_url = models.URLField(help_text="Lien Youtube la")
    pdf_file = models.FileField(upload_to='lesson_pdfs/', blank=True, null=True, validators=[FileExtensionValidator(['pdf'])], help_text="Ajoute yon dokiman PDF pou leson an si sa nesese.")
    order = models.PositiveIntegerField(default=0, help_text="LÃ²d leson an nan kou a (egz: 1, 2, 3...)")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

# ======================================================
# --- 3. MODÃˆL PWOFIL ---
# ======================================================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(default='default.jpg', upload_to='profile_pics')
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True, help_text="Paraf nimerik (PNG transparan rekÃ²mande)")
    bio = models.TextField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'Profil de {self.user.username}'

# ======================================================
# --- 4. MODÃˆL POU KÃ’MANTÃˆ ---
# ======================================================
class Comment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f'KÃ²mantÃ¨ {self.user.username} sou {self.lesson.title}'

# ======================================================
# --- 5. MODÃˆL FOWÃ’M ---
# ======================================================
class ForumTopic(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ForumPost(models.Model):
    topic = models.ForeignKey(ForumTopic, related_name='posts', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# ======================================================
# --- 6. MODÃˆL SEMINÃˆ AK GALRI ---
# ======================================================
class Seminar(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_event = models.DateField()
    period = models.CharField(max_length=100, help_text="Ex: Janvye - Mas 2026")
    video_url = models.URLField(blank=True, null=True, help_text="Link Youtube videyo seminÃ¨ a")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.period})"

    @property
    def primary_image(self):
        return self.images.first()

    @property
    def registered_count(self):
        return self.registrations.count()

class SeminarImage(models.Model):
    seminar = models.ForeignKey(Seminar, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='seminars/')


class SeminarRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seminar_registrations')
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE, related_name='registrations')
    motivation = models.TextField(blank=True, help_text="Poukisa ou vle patisipe nan seminÃ¨ sa a?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'seminar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.seminar.title}"

# ======================================================
# --- 7. MODÃˆL POU PWOGRÃˆ ---
# ======================================================
class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')

# ======================================================
# --- 8. SISTÃˆM QUIZ ---
# ======================================================
class Quiz(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=255)
    pass_score = models.IntegerField(default=70)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Quizzes"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return self.text[:50]

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    date_attempted = models.DateTimeField(auto_now_add=True)

    def can_retry(self):
        return timezone.now() >= self.date_attempted + timedelta(hours=12)

# ======================================================
# --- 9. ENSKRIPSYON AK PEMAN ---
# ======================================================
class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    date_enrolled = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)
    screenshot = models.ImageField(upload_to='enrollment_proofs/', blank=True, null=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

# ======================================================
# --- 10. NOTIFIKASYON ---
# ======================================================
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# ======================================================
# --- 11. AKTYALITE (Blog) ---
# ======================================================
class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# ======================================================
# --- 12. SÃˆTIFIKA ---
# ======================================================
class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    certificate_code = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.certificate_code:
            self.certificate_code = f"AJF-{self.user.id}-{self.course.id}-{timezone.now().strftime('%y%m%d')}"
        super().save(*args, **kwargs)

# ======================================================
# --- 13. SISTÃˆM PEMAN PWOFEZÃˆ ---
# ======================================================
class Payout(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="PwofesÃ¨")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Kou")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montan Peye")
    month = models.DateField(help_text="Chwazi mwa w ap peye a (egz: 2026-04-01)", verbose_name="Pou mwa")
    date_paid = models.DateTimeField(auto_now_add=True, verbose_name="Dat Peman")

    class Meta:
        verbose_name = "Peman PwofesÃ¨"
        verbose_name_plural = "Peman PwofesÃ¨ yo"

    def __str__(self):
        return f"{self.instructor.username} - {self.amount} HTG"

class ServiceOffering(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.TextField()
    details = models.TextField(blank=True)
    icon_class = models.CharField(max_length=100, default='fas fa-briefcase')
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'title']

    def __str__(self):
        return self.title


class ServiceInquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'Nouvo'),
        ('contacted', 'Kontakte'),
        ('closed', 'Femen'),
    ]

    service = models.ForeignKey(ServiceOffering, on_delete=models.SET_NULL, null=True, blank=True, related_name='inquiries')
    requested_service = models.CharField(max_length=255, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    company = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.requested_service or self.service or 'Inquiry'}"


class CourseReview(models.Model):
    STAR_CHOICES = [(i, f'{i} etwal') for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    stars = models.PositiveSmallIntegerField(choices=STAR_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.course.title} - {self.stars}/5"


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    whatsapp_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.name


class VisitorSession(models.Model):
    ip_address = models.CharField(max_length=64)
    user_agent = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    visits_count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('ip_address', 'user_agent')
        ordering = ['-last_seen']

    def __str__(self):
        return f"{self.ip_address} ({self.visits_count})"


Event = Seminar


