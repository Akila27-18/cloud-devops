from django.db import models
from django.conf import settings
from django.db import transaction


class Course(models.Model):
    CATEGORY_CHOICES = [
        ('Generative AI', 'Generative AI'),
        ('IT Certifications', 'IT Certifications'),
        ('Data Science', 'Data Science'),
        ('DevOps', 'DevOps'),
        ('Web Development', 'Web Development'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.IntegerField(default=399)
    rating = models.FloatField(default=4.6)
    rating_count = models.IntegerField(default=1063)
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES, default='Generative AI')
    thumbnail_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    # NEW: Instructor field
   # courses/models.py
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        null=True, blank=True   # <-- allows existing rows to stay empty
    )

    def __str__(self):
        return self.title


class Review(models.Model):
    course = models.ForeignKey(Course, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} on {self.course.title}"

    class Meta:
        indexes = [
            models.Index(fields=["rating"]),
            models.Index(fields=["course"]),
        ]


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True)

    def embed_url(self):
        if "watch?v=" in self.video_url:
            return self.video_url.replace("watch?v=", "embed/")
        if "youtu.be" in self.video_url:
            video_id = self.video_url.split("/")[-1]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.video_url

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0)  # percentage completed

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

    def completed_percentage(self):
        return round(self.progress, 0)

    def is_complete(self):
        return self.progress >= 100


class LessonCompletion(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="completed_lessons")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("enrollment", "lesson")

    def __str__(self):
        return f"{self.enrollment.user.username} completed {self.lesson.title}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            total_lessons = self.enrollment.course.lessons.count()
            completed = self.enrollment.completed_lessons.count()
            if total_lessons > 0:
                self.enrollment.progress = (completed / total_lessons) * 100
                self.enrollment.save(update_fields=["progress"])