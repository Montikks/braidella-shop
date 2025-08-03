from django.contrib import admin
from .models import Category, Color, Product, Variant, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "ordering")
    list_editable = ("ordering",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "hex_code")
    search_fields = ("name",)


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1
    fields = ("color", "length_cm", "sku", "price", "stock", "active", "ordering")
    autocomplete_fields = ("color",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_main", "ordering")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "active", "updated")
    list_filter = ("active", "category")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [VariantInline, ProductImageInline]
