# core/views.py
from django.shortcuts import render
from courses.models import Course
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from courses.models import Course
from accounts.models import CustomUser

# core/views.py
from django.shortcuts import render, get_object_or_404
from .models import CaseStudy

def case_study_list(request):
    studies = CaseStudy.objects.order_by('-created_at')
    return render(request, 'core/case_study_list.html', {'studies': studies})

def case_study_detail(request, slug):
    study = get_object_or_404(CaseStudy, slug=slug)
    return render(request, 'core/case_study_detail.html', {'study': study})


from .models import CaseStudy

def home(request):
    # Top 5 courses by rating
    trending = Course.objects.order_by('-rating')[:5]

    # Latest 10 Generative AI courses
    ai_courses = Course.objects.filter(category='Generative AI').order_by('-created_at')[:10]

    # Banner course for gift (first trending course)
    banner_course = trending[0] if trending else None

    # Latest case study
    latest_case = CaseStudy.objects.order_by('-created_at').first()

    context = {
        "trending": trending,
        "ai_courses": ai_courses,
        "banner_course": banner_course,  # pass to template
        "study": latest_case,            # pass to footer
    }
    return render(request, "core/home.html", context)


from accounts.models import CustomUser
from courses.models import Course, Enrollment

def business_page(request):
    context = {
        "total_users": CustomUser.objects.count(),
        "total_instructors": CustomUser.objects.filter(is_instructor=True).count(),
        "total_courses": Course.objects.count(),
        "total_enrollments": Enrollment.objects.count(),
    }
    return render(request, "core/business.html", context)

def teach_page(request):
    return render(request, "core/teach.html")

# ==================================================
# GIFT COURSE
# ==================================================
def gift_course(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == "POST":
        recipient_email = request.POST.get("recipient_email")
        message_text = request.POST.get("message", "")
        sender_name = request.user.username if request.user.is_authenticated else "A friend"

        if not recipient_email:
            messages.error(request, "Please provide a valid email address.")
            return redirect("core:gift_course", slug=slug)

        # Build email content
        subject = f"{sender_name} sent you a course gift!"
        message = f"Hi!\n\n{sender_name} has gifted you the course '{course.title}'.\n\n"
        if message_text:
            message += f"Message from {sender_name}: {message_text}\n\n"
        message += f"Enroll now: http://{request.get_host()}/courses/{course.slug}/\n\nEnjoy learning!"

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False,
            )
            messages.success(request, f"Course gift sent to {recipient_email} successfully!")
            return redirect("core:home")
        except Exception as e:
            messages.error(request, f"Failed to send email: {e}")
            return redirect("core:gift_course", slug=slug)

    return render(request, "core/gift_course.html", {"course": course})