from django.urls import path
from . import views

urlpatterns = [
    # --- PAJ PRENSIPAL ---
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # --- SISTÈM AKTYALITE (Blog) ---
    path('news/', views.news_list, name='news_list'),
    path('news/<int:post_id>/', views.post_detail, name='post_detail'),

    # --- TI REZO SOSYAL / FOWÒM ---
    path('forum/', views.forum_home, name='forum_home'),
    path('forum/topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),

    # --- JESTYON KOU & LESON ---
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/enroll/', views.request_enrollment, name='request_enrollment'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),

    # --- QUIZ & SÈTIFIKA ---
    path('course/<int:course_id>/quiz/', views.take_quiz, name='take_quiz'),
    path('course/<int:course_id>/certificate/', views.view_certificate, name='view_certificate'),

    # --- PROFIL & NOTIFIKASYON ---
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('signup/', views.signup, name='signup'),
]