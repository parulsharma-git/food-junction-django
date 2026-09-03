import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from menu.models import Category, FoodItem, FoodItemSize, Offer


GROUP_TAGLINE_ICON = {
    "paranthas": "Paranthas & Chilla",
    "wraps": "Wraps & Rolls",
    "momos": "Momos",
    "burgers": "Burgers",
    "pizza": "Pizza",
    "sandwiches": "Sandwiches & Gym Food",
    "snacks": "Snacks & Fries",
    "maggi-pasta": "Maggi & Pasta",
    "south": "South Indian & More",
    "drinks": "Beverages & Shakes",
}


class Command(BaseCommand):
    help = "Seed the database with the original Food Junction menu data (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset", action="store_true",
            help="Delete all existing categories/items first, then reseed."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fixture_path = Path(__file__).resolve().parent.parent.parent / "fixtures" / "seed_data.json"
        with open(fixture_path) as f:
            data = json.load(f)

        if options["reset"]:
            FoodItem.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing categories & items."))

        # 1) Categories
        cat_by_slug = {}
        for i, g in enumerate(data["groups"]):
            cat, _ = Category.objects.update_or_create(
                slug=g["slug"],
                defaults={
                    "name": g["name"],
                    "tagline": g.get("tagline", ""),
                    "sort_order": i,
                }
            )
            cat_by_slug[g["slug"]] = cat
        self.stdout.write(self.style.SUCCESS(f"Categories ready: {len(cat_by_slug)}"))

        # 2) Food items
        created, updated = 0, 0
        for idx, item in enumerate(data["menu"]):
            cat = cat_by_slug.get(item["group"])
            if not cat:
                continue

            defaults = {
                "subcategory": item.get("cat", cat.name),
                "description": item.get("desc", ""),
                "is_veg": bool(item.get("veg", True)),
                "tag": item.get("tag", "") or "",
                "sort_order": idx,
                "is_available": True,
            }
            if "sizes" not in item:
                defaults["price"] = item.get("price")

            obj, was_created = FoodItem.objects.update_or_create(
                category=cat,
                name=item["name"],
                subcategory=defaults["subcategory"],
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

            if "sizes" in item:
                obj.sizes.all().delete()
                for s_idx, s in enumerate(item["sizes"]):
                    FoodItemSize.objects.create(
                        food_item=obj, label=s["label"], price=s["price"], sort_order=s_idx
                    )

        self.stdout.write(self.style.SUCCESS(f"Food items — created: {created}, updated: {updated}"))

        # 3) A couple of starter offers
        Offer.objects.get_or_create(
            code="FRESH10",
            defaults=dict(title="Instagram Special", discount_percent=10,
                          description="Tag @freshfoodjunction on Instagram for 10% off.")
        )
        Offer.objects.get_or_create(
            code="JUNCTION20",
            defaults=dict(title="Big Order Bonus", discount_percent=20,
                          description="Orders above ₹800 unlock a flat 20% discount.")
        )
        self.stdout.write(self.style.SUCCESS("Offers ready."))
        self.stdout.write(self.style.SUCCESS("Seeding complete."))
