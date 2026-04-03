from django.urls import path
from academy import views


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    # Liy sa a ki manke a:
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('certificate/<int:course_id>/', views.view_certificate, name='view_certificate'),
    path('notifications/', views.notifications_view, name='notifications'),
    # urls.py
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
]
