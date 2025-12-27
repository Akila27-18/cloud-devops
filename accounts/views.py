# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from courses.models import Lesson, Enrollment, LessonCompletion
from .forms import CustomUserCreationForm, CustomAuthenticationForm  # custom forms tied to CustomUser


# Redirect users after login based on role
def redirect_after_login(request):
    user = request.user
    if user.is_authenticated:
        if getattr(user, "is_instructor", False):
            return redirect("instructors:dashboard")
        else:
            return redirect("courses:my_courses")
    return redirect("accounts:login")


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep user logged in
            return redirect("accounts:profile")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, "accounts/change_password.html", {"form": form})


@login_required
def settings_view(request):
    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, "accounts/settings.html", {"form": form})


@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"user": request.user})


@login_required
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=lesson.course)
    LessonCompletion.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    return redirect("courses:detail", slug=lesson.course.slug)


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect_after_login(request)
    else:
        form = CustomAuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after signup
            return redirect_after_login(request)
        else:
            # Debug: show why signup failed
            print(form.errors)  # <-- helpful during dev
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/")