# courses/urls.py
from django import views
from django.urls import path
from .views import catalog, detail
from .views import my_courses, complete_lesson
from . import views

app_name = 'courses'
urlpatterns = [
    path('', catalog, name='catalog'),
    path("add/", views.add_course, name="add_course"),
    
    path('my-courses/', my_courses, name='my_courses'),   # must come before slug
    path('lesson/complete/<int:lesson_id>/', complete_lesson, name='complete_lesson'),
    path('<slug:slug>/', detail, name='detail'),
]