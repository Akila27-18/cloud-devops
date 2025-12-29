from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Course, Lesson, Enrollment, LessonCompletion
from .forms import CourseForm


@login_required
def instructor_dashboard(request):
    # Show only courses owned by the logged-in instructor
    courses = request.user.courses.all()  # thanks to related_name="courses"
    return render(request, "instructors/dashboard.html", {"courses": courses})


@login_required
def add_course(request):
    if not request.user.is_instructor:
        # prevent students from adding courses
        return redirect("core:home")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user   # assign logged-in instructor
            course.save()
            messages.success(request, "Your course has been added successfully!")
            return redirect("instructors:dashboard")  # or course detail page
    else:
        form = CourseForm()

    return render(request, "courses/add_course.html", {"form": form})


@login_required
def detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lessons = course.lessons.order_by("order")
    reviews = course.reviews.order_by("-created_at")

    enrollment = None
    next_lesson = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        if enrollment:
            completed_ids = enrollment.completed_lessons.values_list("lesson_id", flat=True)
            next_lesson = lessons.exclude(id__in=completed_ids).first()

    return render(request, "courses/detail.html", {
        "course": course,
        "lessons": lessons,
        "reviews": reviews,
        "enrollment": enrollment,
        "next_lesson": next_lesson,
    })


@login_required
def my_courses(request):
    # Retrieve all enrollments for the current user
    enrollments = Enrollment.objects.filter(user=request.user).select_related("course")
    return render(request, "courses/my_courses.html", {"enrollments": enrollments})


@login_required
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=lesson.course)

    # Create or fetch the LessonCompletion record for this user and lesson
    LessonCompletion.objects.get_or_create(enrollment=enrollment, lesson=lesson)

    messages.success(request, f"Lesson '{lesson.title}' marked as completed!")
    return redirect("courses:detail", slug=lesson.course.slug)


def catalog(request):
    qs = Course.objects.all().order_by("-created_at")

    # Filters
    category = request.GET.get("category")
    query = request.GET.get("q")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if category:
        qs = qs.filter(category=category)
    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if min_price:
        qs = qs.filter(price__gte=min_price)
    if max_price:
        qs = qs.filter(price__lte=max_price)

    # Pagination logic
    paginator = Paginator(qs, 12)  # Show 12 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "courses/catalog.html", {"courses": page_obj})


@login_required
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    
    # Provide user feedback
    if created:
        messages.success(request, f"Successfully enrolled in {course.title}!")
    else:
        messages.info(request, f"You are already enrolled in {course.title}.")
    
    return redirect("courses:detail", slug=course.slug)
