from django.urls import path
from .views import detail, add

app_name = "cart"
urlpatterns = [
    path("", detail, name="detail"),
    path("add/", add, name="add"),
]
