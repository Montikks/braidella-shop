from django.db import models

class Category(models.Model):
    name = models.CharField("Název", max_length=120)
    slug = models.SlugField("URL (slug)", max_length=140, unique=True)
    description = models.TextField("Popis", blank=True)
    ordering = models.PositiveIntegerField("Pořadí", default=0)

    class Meta:
        ordering = ["ordering", "name"]
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorie"

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField("Název barvy", max_length=80, unique=True)
    hex_code = models.CharField("HEX kód", max_length=7, help_text="#RRGGBB", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Barva"
        verbose_name_plural = "Barvy"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Název", max_length=160)
    slug = models.SlugField("URL (slug)", max_length=180, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name="Kategorie")
    description = models.TextField("Popis", blank=True)
    price = models.DecimalField("Cena (Kč)", max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField("Aktivní", default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Produkt"
        verbose_name_plural = "Produkty"

    def __str__(self):
        return self.name
