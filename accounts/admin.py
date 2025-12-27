
    # accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()


class CourseInline(admin.TabularInline):
    model = Course
    extra = 0
    fields = ("title", "category", "price", "created_at")
    readonly_fields = ("created_at",)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_instructor", "is_staff", "is_superuser")
    list_filter = ("is_instructor", "is_staff", "is_superuser")
    search_fields = ("username", "email")

    fieldsets = UserAdmin.fieldsets + (
        ("Instructor Info", {"fields": ("is_instructor",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Instructor Info", {"fields": ("is_instructor",)}),
    )

    inlines = [CourseInline]  # show courses inline under each instructor