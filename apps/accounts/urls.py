from django.urls import path
from django.contrib.auth import views as auth_views



from . import views

urlpatterns = [
    path('', views.user_login, name='user_login'),

    path('login/', views.user_login, name='user_login'),
    path('register/', views.home, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
    path('profile/', views.user_profile, name='user_profile'),
    path('activate/', views.activate_account, name='activate_account'),

    path('reset_password/', 
        auth_views.PasswordResetView.as_view(template_name ="accounts/password_reset.html"),
        name ="reset_password"),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name ="accounts/password_reset_sent.html"), 
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name ="accounts/password_reset_form.html"), 
        name ="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name = "accounts/password_reset_done.html"), 
        name="password_reset_complete"),
]
