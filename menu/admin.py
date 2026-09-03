from django.contrib import admin
from django.utils.html import format_html
from .models import Category, FoodItem, FoodItemSize, FoodItemImage, Offer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "tagline", "sort_order", "item_count")
    list_editable = ("sort_order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Items"


class FoodItemSizeInline(admin.TabularInline):
    model = FoodItemSize
    extra = 1
    help_text = "Add size/price variants here (e.g. 8-inch / 10-inch pizza). Leave empty and set a single Price above if this item has one size only."


class FoodItemImageInline(admin.TabularInline):
    model = FoodItemImage
    extra = 1
    fields = ("image", "is_primary", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:8px;" />', obj.image.url)
        return "—"
    preview.short_description = "Preview"


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "subcategory", "price_display", "is_veg", "tag", "is_available", "photo_thumb")
    list_filter = ("category", "is_veg", "tag", "is_available")
    list_editable = ("is_available",)
    search_fields = ("name", "subcategory", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [FoodItemSizeInline, FoodItemImageInline]
    fieldsets = (
        ("Basic info", {
            "fields": ("category", "subcategory", "name", "slug", "description")
        }),
        ("Pricing & type", {
            "fields": ("price", "is_veg", "tag"),
            "description": "Leave Price blank if you're using size variants below instead."
        }),
        ("Visibility", {
            "fields": ("is_available", "sort_order")
        }),
    )

    def price_display(self, obj):
        if obj.has_sizes:
            sizes = ", ".join(f"{s.label} ₹{s.price}" for s in obj.sizes.all())
            return sizes
        return f"₹{obj.price}" if obj.price is not None else "—"
    price_display.short_description = "Price"

    def photo_thumb(self, obj):
        img = obj.primary_image
        if img:
            return format_html('<img src="{}" style="height:44px;border-radius:6px;" />', img.image.url)
        return "—"
    photo_thumb.short_description = "Photo"


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "discount_percent", "is_active", "created_at")
    list_editable = ("is_active",)
    search_fields = ("title", "code")

