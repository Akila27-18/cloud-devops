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