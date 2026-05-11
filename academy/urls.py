from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # --- PAJ PRENSIPAL ---
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('contact/', views.contact_page, name='contact_page'),
    path('products/', views.products_page, name='products_page'),
    path('conditions-confidentialite/', views.privacy_page, name='privacy_page'),
    path('rapport-general-site/', views.admin_report, name='admin_report'),
    
    # --- SISTÃˆM AKTYALITE (Blog) ---
    path('news/', views.news_list, name='news_list'),
    path('news/<int:post_id>/', views.post_detail, name='post_detail'),
    path('seminars/<int:seminar_id>/', views.seminar_detail, name='seminar_detail'),
    path('seminars/<int:seminar_id>/register/', views.register_for_seminar, name='register_for_seminar'),

    # --- TI REZO SOSYAL / FOWÃ’M ---
    path('forum/', views.forum_home, name='forum_home'),
    path('forum/topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),

    # --- JESTYON KOU & LESON ---
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/review/', views.submit_course_review, name='submit_course_review'),
    path('course/<int:course_id>/enroll/', views.request_enrollment, name='request_enrollment'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/pdf/', views.lesson_pdf_view, name='lesson_pdf_view'),
    path('lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),

    # --- QUIZ & SÃˆTIFIKA ---
    path('course/<int:course_id>/quiz/', views.take_quiz, name='take_quiz'),
    path('course/<int:course_id>/certificate/', views.view_certificate, name='view_certificate'),

    # --- PROFIL & NOTIFIKASYON ---
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('signup/', views.signup, name='signup'),
    # urls.py
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/add-lesson/', views.add_lesson, name='add_lesson'),
    path('instructor/add-quiz/', views.add_quiz, name='add_quiz'),
    path('instructor/quiz/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
]

# Liy sa a enpÃ²tan anpil pou Django ka afiche siyati ak foto ou upload yo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

