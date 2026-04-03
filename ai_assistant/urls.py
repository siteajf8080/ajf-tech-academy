from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.ai_tutor_chat, name='ai_tutor_chat'),
]