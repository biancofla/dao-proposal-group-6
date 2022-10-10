from django.urls import path, include

urlpatterns = [
    # Local apps.
    path("", include("polls.urls")),
]
