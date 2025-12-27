# checkout/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from courses.models import Course, Enrollment
from .models import Order


@login_required
def mock_checkout(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == "POST":
        with transaction.atomic():
            # Prevent duplicate orders for same user/course
            order, created = Order.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={
                    "amount": course.price,
                    "status": "paid",
                }
            )

            # Auto‑enroll student
            Enrollment.objects.get_or_create(user=order.user, course=order.course)

        return redirect("checkout:success")

    return render(request, "checkout/mock_checkout.html", {"course": course})


@login_required
def success(request):
    return render(request, "checkout/success.html")


@login_required
def cancel(request):
    return render(request, "checkout/cancel.html")