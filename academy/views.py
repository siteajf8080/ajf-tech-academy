import qrcode
import base64
import random
from io import BytesIO
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django import forms
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Enpòtasyon Modèl yo (Mwen ranje Event pou l vin Seminar)
from .models import (
    Course, Lesson, Profile, Comment, Progress, 
    Quiz, Question, Choice, QuizAttempt, Enrollment,
    Notification, Seminar, SeminarImage, Post,
    ForumTopic, ForumPost
)

# ==========================================
#                FÒM YO
# ==========================================

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Mete yon imel ki valid.")
    class Meta:
        model = User
        fields = ("username", "email")

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'telephone']

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

# Fòm pou Fowòm nan
class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['message']

# ==========================================
#                VIEWS YO
# ==========================================

# 1. PAJ AKEY (Landing Page) - Ak Seminè Dinamik
def home(request):
    courses = Course.objects.all().order_by('-id')[:6]
    
    # Sistèm Filtre Peryòd pou Seminè yo
    periode_filter = request.GET.get('periode')
    if periode_filter:
        seminars = Seminar.objects.filter(period=periode_filter, is_active=True).order_by('-date_event')
    else:
        # Montre 3 dènye seminè yo si pa gen filtre
        seminars = Seminar.objects.filter(is_active=True).order_by('-date_event')[:3]
    
    # Rekiperasyon tout peryòd pou Dropdown nan
    all_periods = Seminar.objects.values_list('period', flat=True).distinct()
    
    return render(request, 'academy/home.html', {
        'courses': courses,
        'seminars': seminars,
        'all_periods': all_periods,
        'selected_period': periode_filter
    })

# 2. PAJ AKTYALITE (Blog)
def news_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'academy/news_list.html', {'posts': posts})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'academy/post_detail.html', {'post': post})

# 3. FOWÒM DISKISYON (Pwen #3)
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
        
    return render(request, 'academy/topic_detail.html', {
        'topic': topic,
        'posts': posts,
        'form': form
    })

# 4. NOTIFIKASYON
@login_required
def notifications_view(request):
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    user_notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'academy/notifications.html', {'notifications': user_notifications})

# --- JESTYON KOU AK ENSKRIPSYON ---

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
        has_passed = QuizAttempt.objects.filter(
            user=request.user, 
            quiz=course.quiz, 
            score__gte=course.quiz.pass_score
        ).exists()

    return render(request, 'academy/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'quiz_exists': quiz_exists,
        'has_passed': has_passed
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
                title="Prèv voye 📩",
                message=f"Nou resevwa prèv peman ou pou '{course.title}'. N ap valide sa rapid."
            )
            
            messages.success(request, f"Prèv peman pou kou '{course.title}' la voye ak siksè!")
            return redirect('dashboard')
        else:
            messages.error(request, "Tanpri chwazi yon foto screenshot.")
        
    return render(request, 'academy/payment_info.html', {
        'course': course,
        'enrollment': enrollment
    })

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

    # Ranplase URL Youtube pou Embed
    url = lesson.video_url
    if url:
        if "watch?v=" in url:
            lesson.video_url = url.replace("watch?v=", "embed/")
        elif "youtu.be/" in url:
            video_id = url.split("/")[-1]
            lesson.video_url = f"https://www.youtube.com/embed/{video_id}"

    return render(request, 'academy/lesson_detail.html', {
        'lesson': lesson,
        'comments': comments,
        'form': form
    })

# --- KONTAK AK DASHBOARD ---

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f"Byenveni {user.username} sou AJF-Tech!")
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
            messages.success(request, "Profil ou mete ajou!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=user_profile)

    context = {'u_form': u_form, 'p_form': p_form}
    return render(request, 'academy/edit_profile.html', context)

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
            'is_finished': percentage >= 100 and total_lessons > 0
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

# --- QUIZ AK SÈTIFIKA ---

@login_required
def take_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quiz = get_object_or_404(Quiz, course=course)
    last_attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-date_attempted').first()
    
    if last_attempt and not last_attempt.can_retry():
        temps_ki_rete = (last_attempt.date_attempted + timedelta(hours=12)) - timezone.now()
        heures = int(temps_ki_rete.total_seconds() // 3600)
        minutes = int((temps_ki_rete.total_seconds() % 3600) // 60)
        return render(request, 'academy/quiz_wait.html', {'heures': max(0, heures), 'minutes': max(0, minutes), 'course': course})

    all_questions = list(quiz.questions.all())
    num_to_select = min(len(all_questions), 10)
    selected_questions = random.sample(all_questions, num_to_select)

    if request.method == 'POST':
        score = 0
        question_ids = request.POST.getlist('displayed_questions')
        for q_id in question_ids:
            selected_choice_id = request.POST.get(f'question_{q_id}')
            if selected_choice_id:
                try:
                    choice = Choice.objects.get(id=selected_choice_id, question_id=q_id)
                    if choice.is_correct: score += 1
                except Choice.DoesNotExist: continue
        
        percentage = (score / len(question_ids)) * 100 if question_ids else 0
        QuizAttempt.objects.create(user=request.user, quiz=quiz, score=percentage)
        
        if percentage >= quiz.pass_score:
            Notification.objects.create(
                user=request.user,
                title="Bravo! Quiz Pase 🎉",
                message=f"Ou pase quiz pou '{course.title}' la ak {int(percentage)}%. Sètifika ou pare!"
            )

        return render(request, 'academy/quiz_result.html', {'score': int(percentage), 'passed': percentage >= quiz.pass_score, 'course': course})

    return render(request, 'academy/take_quiz.html', {'quiz': quiz, 'questions': selected_questions, 'course': course})

@login_required
def view_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quiz = getattr(course, 'quiz', None)
    has_passed = QuizAttempt.objects.filter(user=request.user, quiz=quiz, score__gte=quiz.pass_score).exists() if quiz else False

    if not has_passed:
        return redirect('course_detail', course_id=course.id)

    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(f"Verifikasyon AJF-Tech: {request.user.username} - {course.title}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2c3e50", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'academy/certificate.html', {'course': course, 'qr_code': qr_base64, 'user': request.user})