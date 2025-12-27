# clouddevops_lms/urls.py
from django.contrib import admin
from django.urls import path, include
from accounts.views import redirect_after_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('courses/', include('courses.urls')),
    path('accounts/', include('accounts.urls')),
    path("checkout/", include("checkout.urls")),
    path("instructors/", include("instructors.urls")),
    path("redirect-after-login/", redirect_after_login, name="redirect_after_login"),

    
]