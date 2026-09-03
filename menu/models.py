from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Top-level menu group, e.g. Paranthas & Chilla, Pizza, Momos..."""
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    tagline = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


TAG_CHOICES = [
    ("", "No tag"),
    ("bestseller", "Bestseller"),
    ("spicy", "Spicy"),
    ("new", "New"),
]


class FoodItem(models.Model):
    """A single menu item. Belongs to a Category, with an optional finer
    'subcategory' heading (e.g. 'Veg Pizza' vs 'Non-Veg Pizza' inside Pizza)."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    subcategory = models.CharField(
        max_length=120,
        help_text="Finer heading shown on the menu, e.g. 'Veg Burgers', 'Parantha Combo'."
    )
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_veg = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                 help_text="Leave blank if this item uses sizes below instead.")
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, blank=True, default="")
    is_available = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category__sort_order", "sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            i = 1
            while FoodItem.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def has_sizes(self):
        return self.sizes.exists()

    @property
    def display_price(self):
        """Lowest price for display on cards ('From ₹120' style handled in template)."""
        if self.has_sizes:
            return self.sizes.order_by("price").first().price
        return self.price

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()


class FoodItemSize(models.Model):
    """Optional size/price variants, e.g. Pizza 8" / 10"."""
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="sizes")
    label = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "price"]

    def __str__(self):
        return f"{self.food_item.name} — {self.label}"


class FoodItemImage(models.Model):
    """Real photo(s) the owner can upload for a dish. If none uploaded, the
    frontend falls back to its built-in illustration/photo pool automatically."""
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="food_images/")
    is_primary = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_primary", "-uploaded_at"]

    def __str__(self):
        return f"Image for {self.food_item.name}"


class Offer(models.Model):
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=30, unique=True)
    discount_percent = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.code})"

