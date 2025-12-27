from django.db import models
from django.conf import settings
from courses.models import Course
# checkout/models.py
from django.db import models
from django.conf import settings
from courses.models import Course

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # <-- add this

    def __str__(self):
        return f"{self.user} - {self.course} ({self.status})"

