# instructors/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from courses.models import Course, Lesson
from .forms import LessonForm


@login_required
def dashboard(request):
    """
    Instructor dashboard showing only courses owned by the logged-in instructor.
    """
    my_courses = Course.objects.filter(instructor=request.user)
    return render(request, "instructors/dashboard.html", {"courses": my_courses})


@login_required
def add_lesson(request, course_slug):
    """
    Allow an instructor to add a lesson to one of their courses.
    """
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)

    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            return redirect("instructors:dashboard")
    else:
        form = LessonForm()

    return render(request, "instructors/add_lesson.html", {"form": form, "course": course})


@login_required
def edit_lesson(request, lesson_id):
    """
    Allow an instructor to edit a lesson they own.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)

    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect("instructors:dashboard")
    else:
        form = LessonForm(instance=lesson)

    return render(request, "instructors/edit_lesson.html", {"form": form, "lesson": lesson})