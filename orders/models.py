from django.db import models
from catalog.models import Variant

class Order(models.Model):
    # zákazník
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(max_length=120)
    phone = models.CharField(max_length=20)

    # doručení
    DELIVERY_CHOICES = [
        ("address", "Doručení na adresu"),
        ("balikovna", "Balíkovna"),
    ]
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES)

    street = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=80, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)

    balikovna_id = models.CharField(max_length=255, blank=True)   # textový popis (název, zip, adresa)
    balikovna_code = models.CharField(max_length=32, blank=True)  # kód pobočky (např. B39207)

    # ceny
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # stav
    STATUS_CHOICES = [
        ("new", "Nová"),
        ("paid", "Zaplacená"),
        ("canceled", "Zrušená"),
        ("shipped", "Odeslaná"),
        ("done", "Dokončená"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Objednávka #{self.pk} – {self.last_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(Variant, on_delete=models.PROTECT, related_name="order_items")
    name_snapshot = models.CharField(max_length=200)  # název pro případ změn v katalogu
    price = models.DecimalField(max_digits=10, decimal_places=2)  # cena v čase objednávky
    qty = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.name_snapshot} × {self.qty}"
