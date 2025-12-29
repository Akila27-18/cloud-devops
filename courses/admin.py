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
    prepopulated_fields = {"slug": ("title",)}
    inlines = [LessonInline, ReviewInline]

    # ✅ Custom bulk actions
    actions = ["mark_as_featured", "set_price_free"]

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(rating=5.0)  # example: boost rating to highlight
        self.message_user(request, f"{updated} course(s) marked as featured.")

    mark_as_featured.short_description = "Mark selected courses as Featured"

    def set_price_free(self, request, queryset):
        updated = queryset.update(price=0)
        self.message_user(request, f"{updated} course(s) set to FREE.")

    set_price_free.short_description = "Set selected courses to Free"