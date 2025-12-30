# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('business/', views.business_page, name='business'),
    path('teach/', views.teach_page, name='teach'),
    path('gift-course/<slug:slug>/', views.gift_course, name='gift_course'),
    path('gift/<int:course_id>/', views.gift_course, name='gift_course'),
    path('case-studies/', views.case_study_list, name='case_study_list'),
    path('case-study/<slug:slug>/', views.case_study_detail, name='case_study'),
]
