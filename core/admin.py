# core/admin.py

import datetime
from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count
from django.utils.timezone import now

from accounts.models import CustomUser
from courses.models import Course, Enrollment


class CustomAdminSite(admin.AdminSite):
    site_header = "Vetri Academy Admin"
    site_title = "Vetri Academy Admin Portal"
    index_title = "Welcome to Vetri Academy Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("dashboard/", self.admin_view(self.dashboard_view), name="dashboard"),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        # Enrollment counts per month (last 6 months)
        today = now().date()
        six_months_ago = today - datetime.timedelta(days=180)

        enrollment_trends = (
            Enrollment.objects.filter(enrolled_at__gte=six_months_ago)
            .extra(select={'month': "strftime('%%Y-%%m', enrolled_at)"})
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        # ✅ Annotate courses with enrollment_count
        top_courses = (
            Course.objects.annotate(enrollment_count=Count("enrollment"))
            .order_by("-enrollment_count")[:5]
        )

        context = dict(
            self.each_context(request),
            enrollment_trends=enrollment_trends,
            total_users=CustomUser.objects.count(),
            total_instructors=CustomUser.objects.filter(is_instructor=True).count(),
            total_courses=Course.objects.count(),
            total_enrollments=Enrollment.objects.count(),
            top_courses=top_courses,
        )
        return TemplateResponse(request, "admin/dashboard.html", context)

# Instantiate your custom admin site
custom_admin_site = CustomAdminSite(name="custom_admin")