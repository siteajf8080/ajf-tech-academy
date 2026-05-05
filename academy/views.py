import qrcode
import base64
import random
import json
from io import BytesIO
from datetime import timedelta
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django import forms
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.urls import reverse

# EnpÃ²tasyon ModÃ¨l yo
from .models import (
    Course, Lesson, Profile, Comment, Progress, 
    Quiz, Question, Choice, QuizAttempt, Enrollment,
    Notification, Seminar, SeminarImage, SeminarRegistration, Post,
    ForumTopic, ForumPost, Payout
)

# ======================================================
# --- 1. FÃ’M YO (FORMS) ---
# ======================================================

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Mete yon imel ki valid.")
    class Meta:
        model = User
        fields = ("username", "email")

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'telephone', 'signature']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Poze keksyon ou la...', 
                'rows': 3, 
                'class': 'form-control',
                'style': 'border-radius: 8px;'
            }),
        }

class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['message']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['course', 'title', 'content', 'video_url', 'pdf_file', 'order']
        labels = {
            'course': 'Chwazi Kou a',
            'title': 'Tit Leson an',
            'content': 'Kontni (Teks/Deskripsyon)',
            'video_url': 'Link Videyo (YouTube)',
            'order': 'Nimewo lÃ²d (Egz: 1, 2...)'
        }
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(LessonForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['course'].queryset = Course.objects.filter(instructor=user)

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['course', 'title', 'pass_score']
        labels = {
            'course': 'Chwazi Kou a',
            'title': 'Tit Quiz la',
            'pass_score': 'NÃ²t pou pasaj (%)',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['course'].queryset = Course.objects.filter(instructor=user)

# NOUVO FÃ’M POU KESYON
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']
        labels = {'text': 'Kesyon an'}
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ekri kesyon an la...'})
        }

# ======================================================
# --- 2. FONKSYON OTOMATIZASYON ---
# ======================================================

def send_certificate_email(user, course, qr_code_base64, ceo_signature, instructor_signature):
    context = {
        'user': user,
        'course': course,
        'qr_code': qr_code_base64,
        'ceo_signature': ceo_signature,
        'instructor_signature': instructor_signature,
        'date_today': timezone.now(),
    }

    subject = f"FÃ©licitations! Votre certificat AJF-Tech : {course.title}"
    message = (
        f"Bonjour {user.first_name or user.username}\n\n"
        f"FÃ©licitations ! Vous avez rÃ©ussi l'examen pou kou '{course.title}' sou platfÃ²m AJF-Tech la."
    )

    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

    try:
        from xhtml2pdf import pisa

        html_string = render_to_string('academy/certificate.html', context)
        result = BytesIO()
        pisa_status = pisa.CreatePDF(BytesIO(html_string.encode("UTF-8")), dest=result)

        if not pisa_status.err:
            pdf_file = result.getvalue()
            filename = f"Certificat_AJF_{user.username}.pdf"
            email.attach(filename, pdf_file, 'application/pdf')
    except Exception as e:
        print(f"PDF certificate skipped: {e}")

    try:
        email.send()
    except Exception as e:
        print(f"ErÃ¨ nan voye imel sÃ¨tifika: {e}")

# ======================================================
# --- 3. VIEWS YO ---
# ======================================================

def home(request):
    courses = Course.objects.all().order_by('-id')[:6]
    recent_posts = Post.objects.all().order_by('-created_at')[:3]
    periode_filter = request.GET.get('periode')
    if periode_filter:
        seminars = Seminar.objects.filter(period=periode_filter, is_active=True).order_by('-date_event')
    else:
        seminars = Seminar.objects.filter(is_active=True).order_by('-date_event')[:3]
    
    all_periods = Seminar.objects.values_list('period', flat=True).distinct()
    
    return render(request, 'academy/home.html', {
        'courses': courses,
        'recent_posts': recent_posts,
        'seminars': seminars,
        'all_periods': all_periods,
        'selected_period': periode_filter
    })


def contact_page(request):
    return render(request, 'academy/contact.html')


def privacy_page(request):
    return render(request, 'academy/privacy.html')


def seminar_detail(request, seminar_id):
    seminar = get_object_or_404(Seminar, id=seminar_id, is_active=True)
    registration = None
    if request.user.is_authenticated:
        registration = SeminarRegistration.objects.filter(user=request.user, seminar=seminar).first()

    event_image = seminar.primary_image.image.url if seminar.primary_image else None
    event_schema = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": seminar.title,
        "description": seminar.description,
        "startDate": seminar.date_event.isoformat(),
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "eventStatus": "https://schema.org/EventScheduled",
        "organizer": {
            "@type": "Organization",
            "name": "AJF-Tech",
            "url": "https://ajftech.tech",
        },
        "location": {
            "@type": "Place",
            "name": "AJF-Tech Seminar",
            "address": {
                "@type": "PostalAddress",
                "addressCountry": "HT",
            },
        },
        "url": request.build_absolute_uri(reverse('seminar_detail', args=[seminar.id])),
    }
    if event_image:
        event_schema["image"] = [request.build_absolute_uri(event_image)]

    return render(request, 'academy/seminar_detail.html', {
        'seminar': seminar,
        'registration': registration,
        'event_schema': json.dumps(event_schema),
    })


@login_required
def register_for_seminar(request, seminar_id):
    seminar = get_object_or_404(Seminar, id=seminar_id, is_active=True)
    registration, created = SeminarRegistration.objects.get_or_create(
        user=request.user,
        seminar=seminar,
    )

    if request.method == 'POST':
        registration.motivation = request.POST.get('motivation', '').strip()
        registration.save()
        if created:
            Notification.objects.create(
                user=request.user,
                title="Enskripsyon seminÃ¨ konfime",
                message=f"Ou enskri pou seminÃ¨ '{seminar.title}' la pou dat {seminar.date_event:%d/%m/%Y}.",
                url=reverse('seminar_detail', args=[seminar.id]),
            )
            messages.success(request, "Enskripsyon ou anrejistre. N ap tann ou nan seminÃ¨ a.")
        else:
            messages.success(request, "Enskripsyon seminÃ¨ a deja sou kont ou. Nou mete mesaj ou a ajou.")
        return redirect('seminar_detail', seminar_id=seminar.id)

    return redirect('seminar_detail', seminar_id=seminar.id)

@login_required
def instructor_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Ou pa gen pÃ¨misyon pou wÃ¨ paj sa a.")
        return redirect('home')

    my_courses = Course.objects.filter(instructor=request.user).annotate(
        total_students=Count('enrollment', filter=Q(enrollment__is_active=True))
    )
    
    total_instructor_revenue = Decimal('0.0')
    total_students = 0
    for course in my_courses:
        course.gross_revenue = course.total_students * course.price
        course.instructor_share = course.gross_revenue * Decimal('0.5')
        total_students += course.total_students
        total_instructor_revenue += course.instructor_share

    return render(request, 'academy/instructor_dashboard.html', {
        'courses': my_courses,
        'total_students': total_students,
        'total_revenue': total_instructor_revenue,
        'instructor_share_pct': 50,
        'ajf_share_pct': 50
    })

@login_required
def add_lesson(request):
    if not request.user.is_staff:
        messages.error(request, "Ou pa gen pÃ¨misyon pou ajoute leson.")
        return redirect('home')

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            lesson = form.save()
            messages.success(request, f"Leson '{lesson.title}' la ajoute ak siksÃ¨!")
            return redirect('instructor_dashboard')
    else:
        form = LessonForm(user=request.user)
    return render(request, 'academy/add_lesson.html', {'form': form})

@login_required
def add_quiz(request):
    if not request.user.is_staff:
        messages.error(request, "Ou pa gen pÃ¨misyon.")
        return redirect('home')

    if request.method == 'POST':
        form = QuizForm(request.POST, user=request.user)
        if form.is_valid():
            quiz = form.save()
            messages.success(request, "Quiz la kreye! Kounye a, ajoute kesyon yo.")
            # Redireksyon dirÃ¨k pou pwofesÃ¨ a ka kÃ²manse ajoute kesyon yo
            return redirect('add_question', quiz_id=quiz.id)
    else:
        form = QuizForm(user=request.user)
    return render(request, 'academy/add_quiz.html', {'form': form})

# NOUVO VIEW POU AJOUTE KESYON AK CHWA
@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Sekirite: SÃ¨lman mÃ¨t kou a ki ka modifye
    if quiz.course.instructor != request.user:
        messages.error(request, "Ou pa gen dwa modifye quiz sa a.")
        return redirect('instructor_dashboard')

    if request.method == 'POST':
        q_form = QuestionForm(request.POST)
        if q_form.is_valid():
            question = q_form.save(commit=False)
            question.quiz = quiz
            question.save()

            # Rekipere lis repons yo ak radyo bouton ki di kilÃ¨s ki bon an
            choice_texts = request.POST.getlist('choice_text')
            correct_choice_index = request.POST.get('is_correct') # valÃ¨ ap "0", "1", "2" etc.

            for i, text in enumerate(choice_texts):
                if text.strip(): # si bwat la pa vid
                    Choice.objects.create(
                        question=question,
                        text=text,
                        is_correct=(str(i) == correct_choice_index)
                    )
            
            messages.success(request, "Kesyon an ajoute!")
            if 'add_another' in request.POST:
                return redirect('add_question', quiz_id=quiz.id)
            return redirect('instructor_dashboard')
    else:
        q_form = QuestionForm()

    return render(request, 'academy/add_question.html', {'q_form': q_form, 'quiz': quiz})

def news_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'academy/news_list.html', {'posts': posts})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'academy/post_detail.html', {'post': post})

@login_required
def forum_home(request):
    topics = ForumTopic.objects.all().order_by('-created_at')
    return render(request, 'academy/forum_home.html', {'topics': topics})

@login_required
def topic_detail(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    posts = topic.posts.all().order_by('created_at')
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.topic = topic
            new_post.user = request.user
            new_post.save()
            return redirect('topic_detail', topic_id=topic.id)
    else:
        form = ForumPostForm()
    return render(request, 'academy/topic_detail.html', {'topic': topic, 'posts': posts, 'form': form})

@login_required
def notifications_view(request):
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    user_notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'academy/notifications.html', {'notifications': user_notifications})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(user=request.user, course=course, is_active=True).first()
    if not enrollment:
        return redirect('request_enrollment', course_id=course.id)
    
    lessons = course.lessons.all()
    quiz_exists = hasattr(course, 'quiz') 
    has_passed = False
    if quiz_exists:
        has_passed = QuizAttempt.objects.filter(user=request.user, quiz=course.quiz, score__gte=course.quiz.pass_score).exists()

    return render(request, 'academy/course_detail.html', {
        'course': course, 'lessons': lessons, 'quiz_exists': quiz_exists, 'has_passed': has_passed
    })

@login_required
def request_enrollment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    
    if enrollment.is_active:
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        message = request.POST.get('message')
        screenshot = request.FILES.get('screenshot')
        if screenshot:
            enrollment.message = message
            enrollment.screenshot = screenshot
            enrollment.save()
            
            Notification.objects.create(
                user=request.user, 
                title="PrÃ¨v voye ðŸ“©", 
                message=f"Nou resevwa prÃ¨v peman ou pou '{course.title}'."
            )
            messages.success(request, "PrÃ¨v peman voye! Tann validasyon.")
            return redirect('dashboard')
        else:
            messages.error(request, "Chwazi yon screenshot.")
            
    return render(request, 'academy/payment_info.html', {'course': course, 'enrollment': enrollment})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = Enrollment.objects.filter(user=request.user, course=lesson.course, is_active=True).exists()
    if not enrollment:
        return redirect('request_enrollment', course_id=lesson.course.id)

    comments = lesson.comments.filter(parent=None).order_by('-created_at')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.lesson = lesson
            new_comment.user = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                new_comment.parent = Comment.objects.get(id=parent_id)
            new_comment.save()
            return redirect('lesson_detail', lesson_id=lesson.id)
    else:
        form = CommentForm()

    # Lojik pou YouTube Embed
    url = lesson.video_url
    if url:
        if "watch?v=" in url:
            lesson.video_url = url.replace("watch?v=", "embed/")
        elif "youtu.be/" in url:
            video_id = url.split("/")[-1]
            lesson.video_url = f"https://www.youtube.com/embed/{video_id}"

    return render(request, 'academy/lesson_detail.html', {'lesson': lesson, 'comments': comments, 'form': form})

@login_required
def lesson_pdf_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = Enrollment.objects.filter(user=request.user, course=lesson.course, is_active=True).exists()
    if not enrollment:
        return redirect('request_enrollment', course_id=lesson.course.id)

    if not lesson.pdf_file:
        raise Http404('PDF sa a pa disponib.')

    response = FileResponse(lesson.pdf_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{lesson.pdf_file.name.split("/")[-1]}"'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    response['Cache-Control'] = 'private, no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    return response

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile(request):
    Profile.objects.get_or_create(user=request.user)
    return render(request, 'academy/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=user_profile)
    return render(request, 'academy/edit_profile.html', {'u_form': u_form, 'p_form': p_form})

@login_required
def dashboard(request):
    active_enrollments = Enrollment.objects.filter(user=request.user, is_active=True)
    pending_enrollments = Enrollment.objects.filter(user=request.user, is_active=False)
    course_data = []
    for enr in active_enrollments:
        course = enr.course
        total_lessons = course.lessons.count()
        completed_lessons = Progress.objects.filter(user=request.user, lesson__course=course).count()
        percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        course_data.append({
            'course': course, 
            'percentage': int(percentage), 
            'is_finished': percentage >= 100,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons
        })

    return render(request, 'academy/dashboard.html', {
        'course_data': course_data, 
        'pending_enrollments': pending_enrollments, 
        'user': request.user
    })

@login_required
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    Progress.objects.get_or_create(user=request.user, lesson=lesson)
    return redirect('course_detail', course_id=lesson.course.id)

@login_required
def take_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quiz = get_object_or_404(Quiz, course=course)
    
    last_attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-date_attempted').first()
    if last_attempt and not last_attempt.can_retry() and last_attempt.score < quiz.pass_score:
        return render(request, 'academy/quiz_wait.html', {'course': course})

    all_questions = list(quiz.questions.all())
    selected_questions = random.sample(all_questions, min(len(all_questions), 10))

    if request.method == 'POST':
        score = 0
        question_ids = request.POST.getlist('displayed_questions')
        for q_id in question_ids:
            selected_choice_id = request.POST.get(f'question_{q_id}')
            if selected_choice_id:
                choice = Choice.objects.filter(id=selected_choice_id).first()
                if choice and choice.is_correct:
                    score += 1
        
        percentage = (score / len(question_ids)) * 100 if question_ids else 0
        QuizAttempt.objects.create(user=request.user, quiz=quiz, score=percentage)
        
        if percentage >= quiz.pass_score:
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(f"VÃ©rification AJF-Tech: {request.user.username} - ID: {request.user.id}")
            qr.make(fit=True)
            img = qr.make_image(fill_color="#0b1c2c", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            ceo_user = User.objects.filter(is_superuser=True).first()
            ceo_sig = Profile.objects.get(user=ceo_user).signature if ceo_user else None
            inst_sig = Profile.objects.get(user=course.instructor).signature if course.instructor else None
            
            send_certificate_email(request.user, course, qr_base64, ceo_sig, inst_sig)

        return render(request, 'academy/quiz_result.html', {
            'score': int(percentage), 
            'passed': percentage >= quiz.pass_score, 
            'course': course
        })

    return render(request, 'academy/take_quiz.html', {
        'quiz': quiz, 
        'questions': selected_questions, 
        'course': course
    })

@login_required
def view_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    has_passed = QuizAttempt.objects.filter(
        user=request.user, 
        quiz__course=course, 
        score__gte=70
    ).exists()
    
    if not has_passed:
        messages.warning(request, "Ou dwe pase quiz la anvan pou w wÃ¨ sÃ¨tifika a.")
        return redirect('course_detail', course_id=course.id)

    qr = qrcode.QRCode(version=1, box_size=5, border=1)
    qr.add_data(f"AJF-TECH CERT: {request.user.first_name} {request.user.last_name} - {course.title}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0b1c2c", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    ceo_user = User.objects.filter(is_superuser=True).first()
    ceo_sig = Profile.objects.get(user=ceo_user).signature if ceo_user else None
    inst_sig = Profile.objects.get(user=course.instructor).signature if course.instructor else None

    return render(request, 'academy/certificate.html', {
        'course': course, 
        'qr_code': qr_base64, 
        'user': request.user, 
        'date_today': timezone.now(),
        'ceo_signature': ceo_sig,
        'instructor_signature': inst_sig
    })


