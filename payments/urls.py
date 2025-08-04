from django.urls import path
from .views import create_payment   # zatím jen to

app_name = "payments"
urlpatterns = [
    path("create/<int:order_id>/", create_payment, name="create"),
    # return a notify přidáme později
]
