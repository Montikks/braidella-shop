from django.urls import path
from .views import detail, add, update, remove

app_name = "cart"

urlpatterns = [
    path("", detail, name="detail"),
    path("add/", add, name="add"),
    path("update/", update, name="update"),
    path("remove/<int:variant_id>/", remove, name="remove"),
]
