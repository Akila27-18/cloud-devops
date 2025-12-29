from django.urls import path
from . import views

app_name = "instructors"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("course/add/", views.add_course, name="add_course"),
    path("course/<slug:course_slug>/lessons/", views.manage_lessons, name="manage_lessons"),
    path("course/<slug:course_slug>/add_lesson/", views.add_lesson, name="add_lesson"),
    path("lesson/<int:lesson_id>/edit/", views.edit_lesson, name="edit_lesson"),
    path("lesson/<int:lesson_id>/delete/", views.delete_lesson, name="delete_lesson"),
]
