from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("name_snapshot", "price", "qty", "subtotal")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "last_name", "email", "total", "status", "created")
    list_filter = ("status", "created")
    search_fields = ("id", "last_name", "email", "phone", "balikovna_code", "zip_code")
    inlines = [OrderItemInline]
