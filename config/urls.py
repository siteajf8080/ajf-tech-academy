from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 1. Administrasyon AJF-Tech
    path('admin/', admin.site.urls),
    
    # 2. Tout URL ki nan app 'academy' a (Dashboard, Kou, elatriye)
    path('', include('academy.urls')),

    # 3. Sistèm AI Assistant (Si w gen app sa a ki prè)
    path('ai/', include('ai_assistant.urls')),
    
    # 4. SISTÈM OTANTIFIKASYON
    # Login
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # Logout (Django 5.0 rekòmande sa pou sekirite)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 5. JESTYON MODPAS (Password Reset)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]

# 6. KONFIGIRASYON POU FOTO (MEDIA) AK STATIC PANDAN DEVLOPMAN
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)