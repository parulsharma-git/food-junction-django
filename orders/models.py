from django.db import models
from django.utils.crypto import get_random_string


STATUS_CHOICES = [
    ("pending", "Pending"),
    ("confirmed", "Confirmed"),
    ("preparing", "Preparing"),
    ("out_for_delivery", "Out for Delivery"),
    ("delivered", "Delivered"),
    ("cancelled", "Cancelled"),
]

PAYMENT_CHOICES = [
    ("cod", "Cash on Delivery"),
    ("online", "Online Payment"),
]


def generate_order_id():
    return "FJ" + get_random_string(6, allowed_chars="0123456789")


class Order(models.Model):
    order_id = models.CharField(max_length=20, unique=True, default=generate_order_id, editable=False)

    # Customer / delivery details
    customer_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    landmark = models.CharField(max_length=160, blank=True)
    note = models.CharField(max_length=250, blank=True)

    # Payment
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")
    is_paid = models.BooleanField(default=False, help_text="Manually mark true once online payment is confirmed.")

    # Pricing snapshot
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    promo_code = models.CharField(max_length=30, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_id} — {self.customer_name} (₹{self.total})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    food_item = models.ForeignKey("menu.FoodItem", on_delete=models.SET_NULL, null=True, blank=True)

    # snapshots so historical orders stay correct even if the menu item later changes/deletes
    name = models.CharField(max_length=160)
    size_label = models.CharField(max_length=30, blank=True)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.name}"

