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
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name="Kategorie"
    )
    description = models.TextField("Popis", blank=True)
    price = models.DecimalField("Cena (Kč)", max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField("Aktivní", default=True)
    created = models.DateTimeField("Vytvořeno", auto_now_add=True)
    updated = models.DateTimeField("Upraveno", auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Produkt"
        verbose_name_plural = "Produkty"

    def __str__(self):
        return self.name


class Variant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants", verbose_name="Produkt"
    )
    color = models.ForeignKey(
        Color, on_delete=models.PROTECT, related_name="variants", verbose_name="Barva"
    )
    length_cm = models.PositiveIntegerField("Délka (cm)", default=60)
    sku = models.CharField("SKU", max_length=50, blank=True)
    price = models.DecimalField(
        "Cena variace (Kč)", max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Když prázdné, použije se cena produktu"
    )
    stock = models.PositiveIntegerField("Sklad (ks)", default=0)
    active = models.BooleanField("Aktivní", default=True)
    ordering = models.PositiveIntegerField("Pořadí", default=0)

    class Meta:
        ordering = ["product", "ordering", "color__name", "length_cm"]
        verbose_name = "Varianta"
        verbose_name_plural = "Varianty"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "color", "length_cm"], name="uniq_product_color_length"
            )
        ]

    def __str__(self):
        return f"{self.product.name} • {self.color.name} • {self.length_cm} cm"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Produkt"
    )
    image = models.ImageField("Obrázek", upload_to="products/%Y/%m/")
    alt_text = models.CharField("ALT text", max_length=160, blank=True)
    is_main = models.BooleanField("Hlavní obrázek", default=False)
    ordering = models.PositiveIntegerField("Pořadí", default=0)
    created = models.DateTimeField("Nahráno", auto_now_add=True)

    class Meta:
        ordering = ["product", "ordering", "-created"]
        verbose_name = "Obrázek produktu"
        verbose_name_plural = "Obrázky produktů"

    def __str__(self):
        return f"Obrázek • {self.product.name}"
