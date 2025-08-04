from django.urls import path
from .views import address, review, balikovna_picker

app_name = "checkout"

urlpatterns = [
    path("", address, name="address"),
    path("review/", review, name="review"),
    path("balikovna/picker/", balikovna_picker, name="balikovna_picker"),
]
