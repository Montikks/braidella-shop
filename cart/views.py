from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from catalog.models import Product, Variant

CART_SESSION_KEY = "cart"

def _get_cart(session):
    return session.setdefault(CART_SESSION_KEY, {})

def _key_for(product_id=None, variant_id=None):
    if product_id:
        return f"p:{int(product_id)}"
    if variant_id:
        return f"v:{int(variant_id)}"
    raise ValueError("product_id or variant_id required")

def add(request):
    if request.method != "POST":
        return redirect("cart:detail")

    product_id = request.POST.get("product_id")
    variant_id = request.POST.get("variant_id")
    qty_raw = request.POST.get("qty", "1")

    try:
        qty = max(1, int(qty_raw))
    except ValueError:
        qty = 1

    # Rozhodni, co přidáváme
    if product_id:
        obj = get_object_or_404(Product, pk=product_id, active=True)
        key = _key_for(product_id=product_id)
        name = obj.name
        price = obj.price
    elif variant_id:
        v = get_object_or_404(Variant, pk=variant_id, active=True)
        obj = v
        key = _key_for(variant_id=variant_id)
        name = f"{v.product.name} – {v.color.name} {v.length_cm} cm"
        price = v.price if v.price is not None else v.product.price
    else:
        messages.error(request, "Nebyla uvedena položka.")
        return redirect("cart:detail")

    # (volitelně) kontrola skladu – u Product jen pokud existuje pole stock
    stock = getattr(obj, "stock", None)
    if stock is not None and qty > stock:
        qty = stock
        if qty <= 0:
            messages.error(request, "Položka není skladem.")
            return redirect("cart:detail")

    cart = _get_cart(request.session)
    cart[key] = cart.get(key, 0) + qty
    request.session.modified = True
    messages.success(request, f"Přidáno do košíku: {name} (×{qty})")
    return redirect("cart:detail")

def update(request):
    if request.method != "POST":
        return redirect("cart:detail")

    key = request.POST.get("key")
    qty_raw = request.POST.get("qty", "1")

    try:
        qty = max(0, int(qty_raw))
    except ValueError:
        qty = 1

    cart = _get_cart(request.session)

    # identifikace objektu kvůli kontrole skladů
    obj = None
    if key and key.startswith("p:"):
        pid = int(key.split(":")[1])
        obj = get_object_or_404(Product, pk=pid, active=True)
    elif key and key.startswith("v:"):
        vid = int(key.split(":")[1])
        obj = get_object_or_404(Variant, pk=vid, active=True)

    if obj is not None:
        stock = getattr(obj, "stock", None)
        if stock is not None:
            qty = min(qty, max(0, stock))

    if qty <= 0:
        cart.pop(key, None)
        messages.info(request, "Položka odebrána z košíku.")
    else:
        cart[key] = qty
        messages.success(request, f"Množství upraveno na ×{qty}.")
    request.session.modified = True
    return redirect("cart:detail")

def remove(request, key):
    if request.method != "POST":
        return redirect("cart:detail")
    cart = request.session.get(CART_SESSION_KEY, {})
    if key in cart:
        cart.pop(key)
        request.session.modified = True
        messages.info(request, "Položka odebrána z košíku.")
    return redirect("cart:detail")

def detail(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    items = []
    total = 0

    if cart:
        v_ids = [int(k.split(":")[1]) for k in cart.keys() if k.startswith("v:")]
        p_ids = [int(k.split(":")[1]) for k in cart.keys() if k.startswith("p:")]

        variants = {v.pk: v for v in Variant.objects.filter(pk__in=v_ids).select_related("product", "color")}
        products = {p.pk: p for p in Product.objects.filter(pk__in=p_ids).select_related("category")}

        for key, qty_val in cart.items():
            try:
                qty = int(qty_val)
            except ValueError:
                qty = 1

            if key.startswith("v:"):
                vid = int(key.split(":")[1])
                v = variants.get(vid)
                if not v:
                    continue
                price = v.price if v.price is not None else v.product.price
                subtotal = price * qty
                items.append({
                    "key": key,
                    "kind": "variant",
                    "variant": v,
                    "product": v.product,
                    "qty": qty,
                    "price": price,
                    "subtotal": subtotal,
                    "label": f"{v.product.name} – {v.color.name} {v.length_cm} cm",
                })
                total += subtotal

            elif key.startswith("p:"):
                pid = int(key.split(":")[1])
                p = products.get(pid)
                if not p:
                    continue
                price = p.price
                subtotal = price * qty
                items.append({
                    "key": key,
                    "kind": "product",
                    "product": p,
                    "qty": qty,
                    "price": price,
                    "subtotal": subtotal,
                    "label": p.name,
                })
                total += subtotal

    return render(request, "cart/detail.html", {"items": items, "total": total})
