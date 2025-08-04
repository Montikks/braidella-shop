from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from catalog.models import Variant
from .forms import AddressForm
from orders.models import Order, OrderItem  # ← přidáno

CART_SESSION_KEY = "cart"
CHECKOUT_SESSION_KEY = "checkout_address"


def address(request):
    initial = request.session.get(CHECKOUT_SESSION_KEY, {})
    initial.setdefault("delivery_method", "address")
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            request.session[CHECKOUT_SESSION_KEY] = form.cleaned_data
            request.session.modified = True
            return redirect("checkout:review")
    else:
        form = AddressForm(initial=initial)
    return render(request, "checkout/address.html", {"form": form})


def review(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    if not cart:
        messages.info(request, "Košík je prázdný.")
        return redirect("cart:detail")

    items, total = [], 0
    variants = Variant.objects.filter(pk__in=[int(k) for k in cart.keys()]).select_related("product", "color")
    for v in variants:
        qty = int(cart.get(str(v.pk), 0))
        price = v.price if v.price is not None else v.product.price
        subtotal = price * qty
        items.append({"variant": v, "qty": qty, "price": price, "subtotal": subtotal})
        total += subtotal

    addr = request.session.get(CHECKOUT_SESSION_KEY)
    if not addr:
        messages.info(request, "Vyplňte prosím doručovací údaje.")
        return redirect("checkout:address")

    return render(request, "checkout/review.html", {"items": items, "total": total, "addr": addr})


def balikovna_picker(request):
    return render(request, "checkout/balikovna_picker.html")


def place_order(request):
    # jen POST z rekapitulace
    if request.method != "POST":
        return redirect("checkout:review")

    cart = request.session.get(CART_SESSION_KEY, {})
    if not cart:
        messages.info(request, "Košík je prázdný.")
        return redirect("cart:detail")

    addr = request.session.get(CHECKOUT_SESSION_KEY)
    if not addr:
        messages.info(request, "Vyplňte prosím doručovací údaje.")
        return redirect("checkout:address")

    # načti varianty
    keys = [int(k) for k in cart.keys()]
    variants = {v.pk: v for v in Variant.objects.filter(pk__in=keys).select_related("product", "color")}

    # základní validace skladu
    items_payload = []
    total = 0
    for k in keys:
        v = variants.get(k)
        if not v or not v.active:
            messages.error(request, "Některá varianta už není dostupná.")
            return redirect("cart:detail")
        qty = int(cart[str(k)])
        if v.stock and qty > v.stock:
            messages.error(request, f"Na skladě je jen {v.stock} ks varianty {v.product.name} – {v.color.name} {v.length_cm} cm.")
            return redirect("cart:detail")
        price = v.price if v.price is not None else v.product.price
        subtotal = price * qty
        total += subtotal
        items_payload.append((v, qty, price, subtotal))

    # vytvoř objednávku
    order = Order.objects.create(
        first_name=addr.get("first_name", ""),
        last_name=addr.get("last_name", ""),
        email=addr.get("email", ""),
        phone=addr.get("phone", ""),
        delivery_method=addr.get("delivery_method", "address"),
        street=addr.get("street", ""),
        city=addr.get("city", ""),
        zip_code=addr.get("zip_code", ""),
        balikovna_id=addr.get("balikovna_id", ""),
        balikovna_code=addr.get("balikovna_code", ""),
        total=total,
        status="new",
    )

    # položky a snížení skladu
    for v, qty, price, subtotal in items_payload:
        OrderItem.objects.create(
            order=order,
            variant=v,
            name_snapshot=f"{v.product.name} – {v.color.name} {v.length_cm} cm",
            price=price,
            qty=qty,
            subtotal=subtotal,
        )
        if v.stock is not None:
            v.stock = max(0, v.stock - qty)
            v.save(update_fields=["stock"])

    # vyprázdni košík
    try:
        del request.session[CART_SESSION_KEY]
    except KeyError:
        pass
    request.session.modified = True

    return redirect("checkout:success", order_id=order.id)


def success(request, order_id: int):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "checkout/success.html", {"order": order})
