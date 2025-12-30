from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Avg
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Course, Lesson, Enrollment, LessonCompletion
from .forms import CourseForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from courses.models import Course, Gift
from accounts.models import CustomUser

def gift_course(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == "POST":
        recipient_email = request.POST.get("recipient_email")
        message_text = request.POST.get("message", "")
        sender = request.user if request.user.is_authenticated else None
        sender_name = sender.username if sender else "A friend"

        if not recipient_email:
            messages.error(request, "Please provide a valid email address.")
            return redirect("core:gift_course", slug=slug)

        # Create Gift object
        gift = Gift.objects.create(
            course=course,
            sender=sender,
            recipient_email=recipient_email,
            message=message_text,
        )

        # Render HTML email
        context = {
            "sender_name": sender_name,
            "recipient_email": recipient_email,
            "course": course,
            "message_text": message_text,
            "redeem_url": gift.get_redeem_url(request),
        }
        subject = f"{sender_name} sent you a course gift!"
        html_content = render_to_string("emails/gift_course.html", context)

        try:
            msg = EmailMultiAlternatives(subject, html_content, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            messages.success(request, f"Gift email sent to {recipient_email} successfully!")
            return redirect("core:home")

        except Exception as e:
            messages.error(request, f"Failed to send email: {e}")
            return redirect("core:gift_course", slug=slug)

    return render(request, "core/gift_course.html", {"course": course})

def redeem_gift(request, token):
    gift = get_object_or_404(Gift, token=token, redeemed=False)
    
    # Here you can enroll the recipient, create a user if needed, etc.
    # For example, redirect to course page after marking redeemed
    gift.redeemed = True
    gift.save()

    messages.success(request, f"You have successfully redeemed the course: {gift.course.title}")
    return redirect("courses:detail", slug=gift.course.slug)

# ==================================================
# INSTRUCTOR
# ==================================================

@login_required
def instructor_dashboard(request):
    courses = (
        request.user.courses
        .annotate(
            enrollments_count=Count("enrollments"),
            avg_progress=Avg("enrollments__progress"),
        )
    )
    return render(
        request,
        "instructors/dashboard.html",
        {"courses": courses},
    )

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
            messages.success(request, "Your course has been added successfully!")
            return redirect("instructors:dashboard")
    else:
        form = CourseForm()

    return render(request, "courses/add_course.html", {"form": form})

# ==================================================
# COURSE DETAIL
# ==================================================

@login_required
def detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lessons = list(course.lessons.order_by("order"))
    reviews = course.reviews.order_by("-created_at")

    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()

    completed_ids = []
    next_lesson = None
    locked_lessons = set()

    if enrollment:
        completed_ids = list(enrollment.completed_lessons.values_list("lesson_id", flat=True))
        next_lesson = course.lessons.exclude(id__in=completed_ids).order_by("order").first()

        # 🔒 Lock logic
        unlocked = True
        for lesson in lessons:
            lesson.completed = lesson.id in completed_ids
            if not lesson.completed and not unlocked:
                locked_lessons.add(lesson.id)
            if not lesson.completed:
                unlocked = False

    return render(
        request,
        "courses/detail.html",
        {
            "course": course,
            "lessons": lessons,
            "reviews": reviews,
            "enrollment": enrollment,
            "next_lesson": next_lesson,
            "locked_lessons": locked_lessons,
        },
    )

# ==================================================
# COMPLETE LESSON (AJAX + AUTO-COMPLETE)
# ==================================================

@login_required
def complete_lesson(request, lesson_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=lesson.course)

    # 🔒 Prevent skipping lessons
    previous_lessons = Lesson.objects.filter(course=lesson.course, order__lt=lesson.order)
    incomplete_previous = previous_lessons.exclude(id__in=enrollment.completed_lessons.values("lesson_id")).exists()
    if incomplete_previous:
        return JsonResponse({"error": "Complete previous lessons first"}, status=403)

    completion, created = LessonCompletion.objects.get_or_create(enrollment=enrollment, lesson=lesson)

    if created:
        total = Lesson.objects.filter(course=lesson.course).count()
        completed = LessonCompletion.objects.filter(enrollment=enrollment).count()
        enrollment.progress = round((completed / total) * 100, 2)

        # 🎓 Certificate unlock
        if enrollment.progress == 100:
            enrollment.certificate_issued = True

        enrollment.save()

    return JsonResponse({
        "completed": True,
        "lesson_id": lesson.id,
        "progress": enrollment.progress,
        "certificate": enrollment.progress == 100,
    })

# ==================================================
# MY COURSES
# ==================================================

@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related("course")
    return render(request, "courses/my_courses.html", {"enrollments": enrollments})

# ==================================================
# COURSE CATALOG
# ==================================================

from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Course

def catalog(request):
    qs = Course.objects.all().order_by("-created_at")

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

    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = ["Generative AI", "IT Certifications", "Data Science", "DevOps", "Web Development"]

    context = {
        "courses": page_obj,
        "categories": categories,  # pass to template
    }

    return render(request, "courses/catalog.html", context)


# ==================================================
# ENROLL
# ==================================================

@login_required
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)

    if created:
        messages.success(request, f"You are enrolled in {course.title}")
    else:
        messages.info(request, f"You are already enrolled in {course.title}")

    return redirect("courses:detail", slug=course.slug)

def buy_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    # Implement your purchase logic here
    return render(request, "checkout/checkout.html", {"course": course})
    return render(request, "checkout/checkout.html", {"course": course})
