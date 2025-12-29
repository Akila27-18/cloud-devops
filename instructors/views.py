from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from courses.models import Course, Lesson
from .forms import LessonForm
from courses.forms import CourseForm  # import CourseForm from the courses app




@login_required
def dashboard(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, "instructors/dashboard.html", {"courses": courses})

@login_required
def add_course(request):
    if not request.user.is_instructor:
        return redirect("core:home")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, "Course added successfully!")
            return redirect("instructors:dashboard")
    else:
        form = CourseForm()

    return render(request, "instructors/add_course.html", {"form": form})

@login_required
def manage_lessons(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    lessons = course.lessons.all().order_by("order")
    return render(request, "instructors/manage_lessons.html", {"course": course, "lessons": lessons})

@login_required
def add_lesson(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)

    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, "Lesson added successfully!")
            return redirect("instructors:manage_lessons", course_slug=course.slug)
    else:
        form = LessonForm()

    return render(request, "instructors/add_lesson.html", {"form": form, "course": course})

@login_required
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)

    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")
            return redirect("instructors:manage_lessons", course_slug=lesson.course.slug)
    else:
        form = LessonForm(instance=lesson)

    return render(request, "instructors/edit_lesson.html", {"form": form, "lesson": lesson})

@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    course_slug = lesson.course.slug

    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Lesson deleted successfully!")
        return redirect("instructors:manage_lessons", course_slug=course_slug)

    return render(request, "instructors/delete_lesson.html", {"lesson": lesson})
