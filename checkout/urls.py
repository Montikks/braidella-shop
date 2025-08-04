from django.urls import path
from .views import address, review

app_name = "checkout"
urlpatterns = [
    path("", address, name="address"),   # /checkout/
    path("review/", review, name="review"),
]
