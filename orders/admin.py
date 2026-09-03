from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("food_item", "name", "size_label", "unit_price", "quantity", "line_total_display")
    can_delete = False

    def line_total_display(self, obj):
        return f"₹{obj.line_total}"
    line_total_display.short_description = "Line Total"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "customer_name", "phone", "status_badge", "payment_method",
                     "total", "created_at")
    list_filter = ("status", "payment_method", "is_paid", "created_at")
    list_editable = ()
    search_fields = ("order_id", "customer_name", "phone", "address")
    readonly_fields = ("order_id", "subtotal", "discount", "delivery_fee", "total",
                        "promo_code", "created_at", "updated_at")
    inlines = [OrderItemInline]
    fieldsets = (
        ("Order", {"fields": ("order_id", "status", "created_at", "updated_at")}),
        ("Customer", {"fields": ("customer_name", "phone", "address", "landmark", "note")}),
        ("Payment", {"fields": ("payment_method", "is_paid")}),
        ("Amounts", {"fields": ("subtotal", "discount", "delivery_fee", "promo_code", "total")}),
    )

    def status_badge(self, obj):
        colors = {
            "pending": "#d9a94e", "confirmed": "#3f8f5f", "preparing": "#e6592b",
            "out_for_delivery": "#4a7ed6", "delivered": "#3f8f5f", "cancelled": "#b5342e",
        }
        color = colors.get(obj.status, "#999")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def has_add_permission(self, request):
        # Orders are created by customers through checkout, not manually in admin
        return False

