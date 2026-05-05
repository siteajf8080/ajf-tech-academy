from django.contrib import admin
from django.db import models
from django.db.models import Count, Q
from django.utils.html import format_html, mark_safe
from decimal import Decimal
from django.contrib.admin import DateFieldListFilter

from .models import (
    Course, Lesson, Profile, Comment, Progress, 
    Quiz, Question, Choice, QuizAttempt, Enrollment,
    Seminar, SeminarImage, SeminarRegistration, Notification, Post,
    ForumTopic, ForumPost, Payout
)

# ======================================================
# --- 1. JESTYON SEMINÈ AK FOTO ---
# ======================================================
class SeminarImageInline(admin.TabularInline):
    model = SeminarImage
    extra = 1

@admin.register(Seminar)
class SeminarAdmin(admin.ModelAdmin):
    list_display = ('title', 'period', 'date_event', 'is_active', 'registered_count')
    list_filter = ('period', 'is_active')
    search_fields = ('title', 'description')
    inlines = [SeminarImageInline]

    def registered_count(self, obj):
        return obj.registrations.count()
    registered_count.short_description = 'Enskri yo'


@admin.register(SeminarRegistration)
class SeminarRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'seminar', 'created_at')
    list_filter = ('seminar', 'created_at')
    search_fields = ('user__username', 'user__email', 'seminar__title', 'motivation')
    readonly_fields = ('created_at',)

# ======================================================
# --- 2. SISTÈM PEMAN & ENSKRIPSYON ---
# ======================================================
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'display_screenshot', 'payment_status', 'is_active', 'date_enrolled')
    list_filter = ('is_active', 'course', 'date_enrolled')
    search_fields = ('user__username', 'course__title', 'message')
    list_editable = ('is_active',) 
    readonly_fields = ('display_screenshot_large', 'date_enrolled')
    date_hierarchy = 'date_enrolled'
    actions = ['activate_enrollments', 'deactivate_enrollments']

    def payment_status(self, obj):
        color = 'green' if obj.is_active else '#d32f2f'
        text = 'KONFIME' if obj.is_active else 'PENDING'
        return format_html('<b style="color: {0}; font-size: 10px; text-transform: uppercase;">{1}</b>', color, text)
    payment_status.short_description = 'Status'

    def display_screenshot(self, obj):
        if obj.screenshot:
            try:
                return format_html('<img src="{0}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 8px; border: 1px solid #ddd;" />', obj.screenshot.url)
            except:
                return mark_safe('<span style="color: red;">Erè</span>')
        return mark_safe('<span style="color: #999;">Manke</span>')
    display_screenshot.short_description = 'Prèv'

    def display_screenshot_large(self, obj):
        if obj.screenshot:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-width: 400px; border-radius: 10px;" /></a>', obj.screenshot.url)
        return "Pa gen prèv peman."
    display_screenshot_large.short_description = 'Gwo Aperçu'

    @admin.action(description="Aktive aksè (Peye)")
    def activate_enrollments(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Bloke aksè")
    def deactivate_enrollments(self, request, queryset):
        queryset.update(is_active=False)

# ======================================================
# --- 3. KOU AK LOJIK FINANSYÈ (FILTÈ MWA) ---
# ======================================================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'instructor', 'price', 'get_period_students', 
        'get_period_revenue', 'get_instructor_share', 'get_admin_share'
    )
    
    # Sa a bay filtè "Ce mois-ci" ak "Par instructor" bò dwat la
    list_filter = (
        'instructor', 
        ('enrollment__date_enrolled', DateFieldListFilter),
    )
    search_fields = ('title', 'instructor__username')

    def get_queryset(self, request):
        """Kalkile elèv aktif yo sèlman pou kou sa a ak peryòd ki chwazi a"""
        queryset = super().get_queryset(request)
        
        # Filtre yo nan URL la
        query_params = request.GET
        filters = Q(enrollment__is_active=True)

        for key, value in query_params.items():
            if key.startswith('enrollment__date_enrolled'):
                filters &= Q(**{key: value})

        # Nou asire ke chak kou konte sèlman elèv pa l yo
        queryset = queryset.annotate(
            _period_students=Count(
                'enrollment', 
                filter=filters & Q(enrollment__course__id=models.F('id'))
            )
        )
        return queryset

    def get_period_students(self, obj):
        return format_html('<b style="color: #3b82f6;">{0} moun</b>', obj._period_students)
    get_period_students.short_description = 'Elèv Peye'

    def get_period_revenue(self, obj):
        total = obj._period_students * obj.price
        return format_html('<span style="font-weight: bold;">{0} HTG</span>', total)
    get_period_revenue.short_description = 'Brut (Peryòd)'

    def get_instructor_share(self, obj):
        share = (obj._period_students * obj.price) * Decimal('0.5')
        return format_html('<span style="color: #10b981; font-weight: bold;">{0} HTG</span>', share)
    get_instructor_share.short_description = 'Prof (50%)'

    def get_admin_share(self, obj):
        share = (obj._period_students * obj.price) * Decimal('0.5')
        return format_html('<span style="color: #f59e0b; font-weight: bold;">{0} HTG</span>', share)
    get_admin_share.short_description = 'AJF (50%)'

# ======================================================
# --- 4. ISTORIK PEMAN (PAYOUT) ---
# ======================================================
@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('instructor', 'course', 'amount', 'get_month_display', 'date_paid')
    list_filter = ('instructor', 'month')
    date_hierarchy = 'month'
    
    def get_month_display(self, obj):
        return obj.month.strftime('%B %Y')
    get_month_display.short_description = 'Mwa Peye'

# ======================================================
# --- 5. SISTÈM QUIZ ---
# ======================================================
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

# ======================================================
# --- 6. PWOFIL AK SIYATI ---
# ======================================================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telephone', 'display_signature')
    search_fields = ('user__username', 'telephone')
    
    def display_signature(self, obj):
        if obj.signature:
            try:
                return format_html('<div style="background: white; display: inline-block; padding: 2px; border: 1px solid #ccc; border-radius: 4px;"><img src="{0}" style="height: 35px; width: auto;" /></div>', obj.signature.url)
            except:
                return mark_safe("Siyati pèdi")
        return mark_safe("Manke")
    display_signature.short_description = 'Siyati'

# ======================================================
# --- 7. LESON ---
# ======================================================
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)

# Rès modèl yo pou AJF-Tech
admin.site.register(Notification)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Progress)
admin.site.register(ForumTopic)
admin.site.register(ForumPost)
