# courses/admin.py

from django.contrib import admin
from .models import Course, Lesson, Review, Enrollment, LessonCompletion


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("title", "order", "video_url")
    ordering = ("order",)


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ("user", "rating", "comment", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "rating", "rating_count", "instructor", "created_at")
    list_filter = ("category", "instructor")
    search_fields = ("title", "category", "description")
    prepopulated_fields = {"slug": ("title",)}  # auto-generate slug from title
    inlines = [LessonInline, ReviewInline]      # show lessons & reviews inline


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    ordering = ("course", "order")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "progress", "enrolled_at")
    list_filter = ("course", "user")
    search_fields = ("user__username", "course__title")


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "lesson", "completed_at")
    list_filter = ("lesson", "enrollment")