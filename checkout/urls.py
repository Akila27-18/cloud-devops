from django.urls import path
from .views import mock_checkout, success, cancel

app_name = "checkout"

urlpatterns = [
    path("mock/<slug:slug>/", mock_checkout, name="mock_checkout"),
    path("success/", success, name="success"),
    path("cancel/", cancel, name="cancel"),
]