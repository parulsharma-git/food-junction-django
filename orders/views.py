from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction

from menu.models import FoodItem
from .cart import Cart
from .models import Order, OrderItem


def cart_view(request):
    cart = Cart(request)
    promo = request.session.get("promo_code", "")
    return render(request, "orders/cart.html", {
        "lines": cart.lines(),
        "totals": cart.totals(promo),
    })


@require_POST
def cart_add(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id, is_available=True)
    size_label = request.POST.get("size") or None
    qty = int(request.POST.get("qty", 1))
    cart = Cart(request)
    cart.add(item, size_label=size_label, qty=qty)
    messages.success(request, f"{item.name} added to cart")
    next_url = request.POST.get("next") or "cart"
    return redirect(next_url)


@require_POST
def buy_now(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id, is_available=True)
    size_label = request.POST.get("size") or None
    qty = int(request.POST.get("qty", 1))
    cart = Cart(request)
    cart.add(item, size_label=size_label, qty=qty)
    return redirect("checkout")


@require_POST
def cart_update(request):
    key = request.POST.get("key")
    qty = int(request.POST.get("qty", 1))
    Cart(request).update_qty(key, qty)
    return redirect("cart")


@require_POST
def cart_remove(request):
    key = request.POST.get("key")
    Cart(request).remove(key)
    messages.info(request, "Item removed")
    return redirect("cart")


@require_POST
def cart_promo(request):
    code = request.POST.get("code", "").strip().upper()
    from .cart import PROMO_CODES
    if code in PROMO_CODES:
        request.session["promo_code"] = code
        messages.success(request, f"Promo applied: {int(PROMO_CODES[code]*100)}% off")
    else:
        request.session.pop("promo_code", None)
        messages.error(request, "Invalid promo code")
    return redirect("cart")


def checkout(request):
    cart = Cart(request)
    promo = request.session.get("promo_code", "")
    lines = cart.lines()

    if request.method == "POST":
        if not lines:
            messages.error(request, "Your cart is empty")
            return redirect("menu")

        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        landmark = request.POST.get("landmark", "").strip()
        note = request.POST.get("note", "").strip()
        payment_method = request.POST.get("payment_method", "cod")

        if not (name and phone and address):
            messages.error(request, "Please fill all required fields")
            return render(request, "orders/checkout.html", {"lines": lines, "totals": cart.totals(promo)})

        totals = cart.totals(promo)
        with transaction.atomic():
            order = Order.objects.create(
                customer_name=name, phone=phone, address=address, landmark=landmark, note=note,
                payment_method=payment_method,
                subtotal=totals["subtotal"], discount=totals["discount"],
                delivery_fee=totals["delivery"], total=totals["total"],
                promo_code=totals["promo_code"],
            )
            for line in lines:
                OrderItem.objects.create(
                    order=order, food_item=line["food_item"], name=line["name"],
                    size_label=line["size_label"], unit_price=line["unit_price"], quantity=line["qty"],
                )
        cart.clear()
        request.session.pop("promo_code", None)
        return redirect("order_success", order_id=order.order_id)

    return render(request, "orders/checkout.html", {"lines": lines, "totals": cart.totals(promo)})


def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, "orders/order_success.html", {"order": order})

