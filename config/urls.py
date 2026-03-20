from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Administrasyon an
    path('admin/', admin.site.urls),
    
    # Tout URL ki nan app 'academy' a
    path('', include('academy.urls')),
    
    # --- SISTÈM OTANTIFIKASYON ---
    
    # Paj Login
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # Logout (Depi Django 5.0, li pi bon pou n itilize fòm POST, men si w sou ansyen vèsyon sa ap mache tou)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # --- JESTYON MODPAS (Opsyonèl men pratik) ---
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
]

# --- KONFIGIRASYON POU FOTO (MEDIA) ---
# Sa a enpòtan anpil pou foto screenshot peman yo ka parèt nan navigatè a
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)