# core/urls.py
from django.urls import path
from .views import home , business_page, teach_page

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path("business/", business_page, name="business_page"),
    path("teach/", teach_page, name="teach_page"),

]