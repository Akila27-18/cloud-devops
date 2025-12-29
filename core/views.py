# core/views.py
from django.shortcuts import render
from courses.models import Course

def home(request):
    # Top 5 courses by rating
    trending = Course.objects.order_by('-rating')[:5]

    # Latest 10 Generative AI courses
    ai_courses = Course.objects.filter(category='Generative AI').order_by('-created_at')[:10]

    context = {
        "trending": trending,
        "ai_courses": ai_courses,
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