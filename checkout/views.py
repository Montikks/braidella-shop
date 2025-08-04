from django.shortcuts import render, redirect
from django.contrib import messages
from catalog.models import Variant
from .forms import AddressForm

CART_SESSION_KEY = "cart"
CHECKOUT_SESSION_KEY = "checkout_address"


def address(request):
    initial = request.session.get(CHECKOUT_SESSION_KEY, {})
    initial.setdefault("delivery_method", "address")  # výchozí volba

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
    return render(request, "checkout/review.html", {"items": items, "total": total, "addr": addr})
