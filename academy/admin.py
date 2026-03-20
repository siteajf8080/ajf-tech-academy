from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Course, Lesson, Profile, Comment, Progress, 
    Quiz, Question, Choice, QuizAttempt, Enrollment,
    Seminar, SeminarImage, Notification, Post,
    ForumTopic, ForumPost
)

# --- 1. JESTYON SEMINÈ AK FOTO (Inline) ---
class SeminarImageInline(admin.TabularInline):
    model = SeminarImage
    extra = 3  # Montre 3 bwat vid pa defo pou foto

@admin.register(Seminar)
class SeminarAdmin(admin.ModelAdmin):
    list_display = ('title', 'period', 'date_event', 'is_active')
    list_filter = ('period', 'is_active')
    search_fields = ('title', 'description')
    inlines = [SeminarImageInline]

# --- 2. SISTÈM PEMAN & ENSKRIPSYON ---
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'display_screenshot', 'is_active', 'date_enrolled')
    list_filter = ('is_active', 'course', 'date_enrolled')
    search_fields = ('user__username', 'course__title', 'message')
    list_editable = ('is_active',)
    readonly_fields = ('display_screenshot_large', 'date_enrolled')
    actions = ['activate_enrollments', 'deactivate_enrollments']

    def display_screenshot(self, obj):
        if obj.screenshot:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.screenshot.url)
        return "Pa gen prèv"
    display_screenshot.short_description = 'Screenshot'

    def display_screenshot_large(self, obj):
        if obj.screenshot:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-width: 400px;" /></a>', obj.screenshot.url)
        return "Pa gen prèv peman"
    display_screenshot_large.short_description = 'Aperçu Prèv Peman'

    @admin.action(description="Aktive aksè pou elèv sa yo (Peye)")
    def activate_enrollments(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Bloke aksè pou elèv sa yo")
    def deactivate_enrollments(self, request, queryset):
        queryset.update(is_active=False)

# --- 3. SISTÈM QUIZ (Inline) ---
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'pass_score')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    inlines = [ChoiceInline]
    list_filter = ('quiz',)

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'date_attempted')
    readonly_fields = ('date_attempted',)

# --- 4. FOWÒM DISKISYON ---
class ForumPostInline(admin.TabularInline):
    model = ForumPost
    extra = 1

@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at')
    inlines = [ForumPostInline]

# --- 5. LÒT MODÈL YO ---

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'id')
    search_fields = ('title',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telephone')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'created_at')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed_at')