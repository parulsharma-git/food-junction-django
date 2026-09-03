"""
Session-based cart. Stored server-side in request.session so it persists
across page navigation and survives page reloads, without relying on
client-side localStorage.
"""

from decimal import Decimal
from menu.models import FoodItem

SESSION_KEY = "cart"
DELIVERY_FEE = Decimal("35")
FREE_DELIVERY_ABOVE = Decimal("499")

PROMO_CODES = {
    "FRESH10": Decimal("0.10"),
    "JUNCTION20": Decimal("0.20"),
}


def _line_key(food_item_id, size_label):
    return f"{food_item_id}::{size_label or ''}"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(SESSION_KEY)
        if cart is None:
            cart = {}
            self.session[SESSION_KEY] = cart
        self.cart = cart

    def save(self):
        self.session[SESSION_KEY] = self.cart
        self.session.modified = True

    def add(self, food_item: FoodItem, size_label=None, qty=1):
        unit_price = food_item.price
        if size_label:
            size = food_item.sizes.filter(label=size_label).first()
            if size:
                unit_price = size.price
        elif food_item.has_sizes:
            first_size = food_item.sizes.first()
            size_label = first_size.label
            unit_price = first_size.price

        key = _line_key(food_item.id, size_label)
        if key in self.cart:
            self.cart[key]["qty"] += qty
        else:
            self.cart[key] = {
                "food_item_id": food_item.id,
                "name": food_item.name,
                "size_label": size_label or "",
                "unit_price": str(unit_price),
                "qty": qty,
                "is_veg": food_item.is_veg,
                "category_slug": food_item.category.slug,
            }
        self.save()

    def update_qty(self, key, qty):
        if key in self.cart:
            if qty <= 0:
                del self.cart[key]
            else:
                self.cart[key]["qty"] = qty
            self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        self.cart = {}
        self.save()

    def __len__(self):
        return sum(l["qty"] for l in self.cart.values())

    def lines(self):
        """Returns list of cart lines with resolved FoodItem + computed totals."""
        result = []
        item_ids = [l["food_item_id"] for l in self.cart.values()]
        items_by_id = {i.id: i for i in FoodItem.objects.filter(id__in=item_ids)}
        for key, line in self.cart.items():
            food_item = items_by_id.get(line["food_item_id"])
            unit_price = Decimal(line["unit_price"])
            result.append({
                "key": key,
                "food_item": food_item,
                "name": line["name"],
                "size_label": line["size_label"],
                "unit_price": unit_price,
                "qty": line["qty"],
                "is_veg": line["is_veg"],
                "line_total": unit_price * line["qty"],
            })
        return result

    def subtotal(self):
        return sum((Decimal(l["unit_price"]) * l["qty"] for l in self.cart.values()), Decimal("0"))

    def totals(self, promo_code=None):
        subtotal = self.subtotal()
        discount = Decimal("0")
        applied_code = ""
        if promo_code and promo_code.upper() in PROMO_CODES:
            applied_code = promo_code.upper()
            discount = (subtotal * PROMO_CODES[applied_code]).quantize(Decimal("1"))
        delivery = Decimal("0") if subtotal == 0 or subtotal >= FREE_DELIVERY_ABOVE else DELIVERY_FEE
        total = max(Decimal("0"), subtotal - discount + delivery)
        return {
            "subtotal": subtotal,
            "discount": discount,
            "delivery": delivery,
            "total": total,
            "promo_code": applied_code,
            "free_delivery_gap": max(Decimal("0"), FREE_DELIVERY_ABOVE - subtotal),
            "free_delivery_above": FREE_DELIVERY_ABOVE,
        }
