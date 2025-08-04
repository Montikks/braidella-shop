from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from catalog.models import Variant

CART_SESSION_KEY = "cart"


def _get_cart(session):
    return session.setdefault(CART_SESSION_KEY, {})


def detail(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    items = []
    total = 0

    if cart:
        variants = Variant.objects.filter(pk__in=[int(k) for k in cart.keys()]).select_related("product", "color")
        for v in variants:
            qty = int(cart.get(str(v.pk), 0))
            price = v.price if v.price is not None else v.product.price
            subtotal = price * qty
            items.append({"variant": v, "qty": qty, "price": price, "subtotal": subtotal})
            total += subtotal

    return render(request, "cart/detail.html", {"items": items, "total": total})


def add(request):
    if request.method != "POST":
        return redirect("cart:detail")

    variant_id = request.POST.get("variant_id")
    qty = request.POST.get("qty", "1")
    try:
        qty = int(qty)
    except ValueError:
        qty = 1
    qty = max(1, qty)

    variant = get_object_or_404(Variant, pk=variant_id, active=True)
    cart = _get_cart(request.session)
    key = str(variant.pk)
    cart[key] = cart.get(key, 0) + qty
    request.session.modified = True

    messages.success(
        request,
        f"Přidáno do košíku: {variant.product.name} – {variant.color.name} {variant.length_cm} cm (×{qty})"
    )
    return redirect("cart:detail")


def update(request):
    if request.method != "POST":
        return redirect("cart:detail")

    variant_id = request.POST.get("variant_id")
    qty_raw = request.POST.get("qty", "1")
    try:
        qty = max(0, int(qty_raw))
    except ValueError:
        qty = 1

    variant = get_object_or_404(Variant, pk=variant_id, active=True)
    max_qty = max(0, variant.stock)
    if max_qty > 0:
        qty = min(qty, max_qty)

    cart = _get_cart(request.session)
    key = str(variant.pk)
    if qty <= 0:
        cart.pop(key, None)
        messages.info(request, "Položka odebrána z košíku.")
    else:
        cart[key] = qty
        messages.success(request, f"Množství upraveno na ×{qty}.")
    request.session.modified = True
    return redirect("cart:detail")


def remove(request, variant_id):
    if request.method != "POST":
        return redirect("cart:detail")
    cart = request.session.get(CART_SESSION_KEY, {})
    key = str(int(variant_id))
    if key in cart:
        cart.pop(key)
        request.session.modified = True
        messages.info(request, "Položka odebrána z košíku.")
    return redirect("cart:detail")
