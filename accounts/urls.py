# accounts/urls.py
from django.urls import path
from .views import login_view, signup_view, logout_view
from .views import profile, settings_view, change_password

app_name = "accounts"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile, name="profile"),
    path("settings/", settings_view, name="settings"),
    path("change-password/", change_password, name="change_password"),

 
]