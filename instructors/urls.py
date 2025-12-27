from django.urls import path
from . import views

app_name = "instructors"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("course/<slug:course_slug>/add-lesson/", views.add_lesson, name="add_lesson"),
    path("lesson/<int:lesson_id>/edit/", views.edit_lesson, name="edit_lesson"),
]