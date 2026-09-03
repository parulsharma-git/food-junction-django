"""
Server-side dish visuals. Priority order for any dish:
  1. A real photo the owner uploaded via Django Admin (FoodItemImage) — always wins.
  2. A verified, category-matched real photo (Wikimedia Commons, food-only).
  3. A hand-drawn colour illustration, guaranteed to render even with no network.
This mirrors the logic that used to live in static/js/images.js, now ported
server-side so uploaded admin photos are picked up automatically.
"""

from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()

TAG_LABEL = {"bestseller": "Bestseller", "spicy": "Spicy", "new": "New"}

GROUP_PHOTO_POOL = {
    "paranthas": ["Aaloo Paratha.JPG", "Picture of tasty Gobi paratha.JPG",
                  "Tandoori Aloo Pyaz Parantha.jpg", "Indian Paratha Plate.JPG"],
    "wraps": ["Paneer kathi roll homemade.jpg", "Paratha roll.jpg", "Veg Roll.JPG", "Roll.Veg.jpg"],
    "momos": ["Momo, Nepal.JPG", "Momo 2.jpg", "Steamed Chicken Momo.jpg", "Momo s.jpg"],
    "burgers": ["Cheeseburger.jpg", "Chargrilled Chicken Burger.jpg",
                "Food topic image Veggie burger.jpg",
                "Veggie burger flickr user bradleyj creative commons.jpg"],
    "pizza": ["Slice of pizza.jpg", "Pizza slice 3.jpg", "Pizza slice 4.jpg", "Pizzarium pizza slices.jpg"],
    "sandwiches": ["Grilled cheese sandwich.jpg", "Grilled ham and cheese sandwich.jpg",
                   "Grilled Chicken Sandwich at Wendys.jpg"],
    "snacks": ["French Fries.JPG", "BK-French-Fries.jpg", "French fries with mayonnaise (3487440272).jpg"],
    "maggi-pasta": ["Pasta.jpg", "Spaghetti Bolognese.jpg", "Pasta with meatballs.jpg", "Strozzapreti Pasta.JPG"],
    "south": ["Idli sambar.JPG", "Idli Sambar Chutney in Madras.JPG",
              "South Indian Breakast Idli Vada Sambar Chutney.JPG"],
    "drinks": ["Chocolate milkshake.JPG", "Strawberry milk shake (cropped).jpg"],
}

ITEM_PHOTO_OVERRIDE = {
    "aloo-parantha": "Aaloo Paratha.JPG",
    "gobi-parantha": "Picture of tasty Gobi paratha.JPG",
}

GROUP_ART = {
    "paranthas": '''<svg viewBox="0 0 120 120">
        <ellipse cx="60" cy="78" rx="42" ry="10" fill="#00000022"/>
        <path d="M20 62c0-16 18-30 40-30s40 14 40 30c0 12-18 20-40 20s-40-8-40-20z" fill="#e0a656"/>
        <path d="M20 62c0-16 18-30 40-30s40 14 40 30" fill="none" stroke="#c9822e" stroke-width="3"/>
        <path d="M28 56c8-6 16-8 32-8s24 2 32 8" fill="none" stroke="#a85f1e" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M32 66c9 3 18 4 28 4s19-1 28-4" fill="none" stroke="#a85f1e" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="42" cy="50" r="3" fill="#7a4416"/><circle cx="60" cy="46" r="3" fill="#7a4416"/><circle cx="78" cy="50" r="3" fill="#7a4416"/>
    </svg>''',
    "wraps": '''<svg viewBox="0 0 120 120">
        <ellipse cx="60" cy="98" rx="40" ry="8" fill="#00000022"/>
        <path d="M22 40c0-8 8-14 20-16l58 6c6 1 8 6 6 11L84 92c-3 8-10 10-16 6L26 68c-6-4-6-12-4-18z" fill="#e8c078"/>
        <path d="M32 44l56 8" stroke="#c9822e" stroke-width="3" stroke-linecap="round"/>
        <path d="M28 56c14 10 34 18 52 20" fill="none" stroke="#7fa650" stroke-width="7" stroke-linecap="round" opacity=".85"/>
        <path d="M34 66c12 8 26 14 40 17" fill="none" stroke="#c0392b" stroke-width="6" stroke-linecap="round" opacity=".8"/>
        <path d="M22 40c0-8 8-14 20-16l58 6c6 1 8 6 6 11" fill="none" stroke="#c9822e" stroke-width="3"/>
    </svg>''',
    "momos": '''<svg viewBox="0 0 120 120">
        <ellipse cx="60" cy="96" rx="46" ry="9" fill="#00000022"/>
        <path d="M20 82c0-4 4-6 8-6h64c4 0 8 2 8 6s-4 8-8 8H28c-4 0-8-4-8-8z" fill="#7a5a34"/>
        <path d="M34 82c0-13 11-24 24-24s24 11 24 24c0 4-4 6-8 6-6-2-8-4-16-4s-10 2-16 4c-4 0-8-2-8-6z" fill="#f4e4c8"/>
        <g transform="translate(66,0)"><path d="M34 78c0-11 9-20 20-20s20 9 20 20c0 3-3 5-7 5-5-2-7-3-13-3s-8 1-13 3c-4 0-7-2-7-5z" fill="#f4e4c8"/></g>
        <path d="M46 30c-3-5 3-7 1-13M60 26c-3-5 3-8 1-14M74 30c-3-5 3-7 1-13" stroke="#e8dfcb" stroke-width="3.2" fill="none" stroke-linecap="round" opacity=".65"/>
    </svg>''',
    "burgers": '''<svg viewBox="0 0 120 120">
        <ellipse cx="60" cy="100" rx="44" ry="8" fill="#00000022"/>
        <path d="M18 46c0-16 19-28 42-28s42 12 42 28z" fill="#e0a656"/>
        <circle cx="42" cy="30" r="2.4" fill="#f4e4c8"/><circle cx="60" cy="24" r="2.4" fill="#f4e4c8"/><circle cx="78" cy="30" r="2.4" fill="#f4e4c8"/>
        <rect x="16" y="46" width="88" height="8" rx="3" fill="#7fa650"/>
        <rect x="18" y="55" width="84" height="12" rx="3" fill="#c0392b"/>
        <rect x="16" y="68" width="88" height="14" rx="4" fill="#6b3d20"/>
        <path d="M18 82c4 6 10 8 10 8h64s6-2 10-8z" fill="#e8b923"/>
        <rect x="14" y="88" width="92" height="14" rx="7" fill="#c9822e"/>
    </svg>''',
    "pizza": '''<svg viewBox="0 0 120 120">
        <ellipse cx="60" cy="100" rx="46" ry="8" fill="#00000022"/>
        <path d="M60 14 L104 96 L16 96 Z" fill="#e8c078"/>
        <path d="M60 14 L98 88 L22 88 Z" fill="#e04a2b"/>
        <path d="M60 14 L94 82 L26 82 Z" fill="#f2c879"/>
        <circle cx="55" cy="42" r="6" fill="#c0392b"/><circle cx="72" cy="54" r="6" fill="#c0392b"/><circle cx="48" cy="62" r="6" fill="#c0392b"/><circle cx="64" cy="70" r="5" fill="#c0392b"/>
        <circle cx="60" cy="50" r="2" fill="#3f8f5f"/><circle cx="50" cy="46" r="2" fill="#3f8f5f"/><circle cx="76" cy="66" r="2" fill="#3f8f5f"/><circle cx="42" cy="70" r="2" fill="#3f8f5f"/>
        <path d="M60 14 L104 96 L16 96 Z" fill="none" stroke="#c9822e" stroke-width="2.5"/>
    </svg>''',
    "sandwiches": '''<svg viewBox="0 0 120 120">
        <ellipse cx="60" cy="100" rx="44" ry="8" fill="#00000022"/>
        <path d="M60 20 L100 92 L20 92 Z" fill="#e8c078"/>
        <rect x="26" y="70" width="68" height="8" fill="#7fa650"/>
        <rect x="30" y="60" width="60" height="8" fill="#c0392b"/>
        <rect x="34" y="50" width="52" height="8" fill="#e8b923"/>
        <path d="M60 20 L100 92 L20 92 Z" fill="none" stroke="#c9822e" stroke-width="2.5"/>
    </svg>''',
    "snacks": '''<svg viewBox="0 0 120 120">
        <ellipse cx="62" cy="100" rx="40" ry="8" fill="#00000022"/>
        <path d="M34 50 L86 50 L78 98 L42 98 Z" fill="#c0392b"/>
        <path d="M34 50 L86 50 L83 60 L37 60 Z" fill="#e04a2b"/>
        <rect x="40" y="18" width="8" height="46" rx="3" fill="#f2c879" transform="rotate(-6 44 41)"/>
        <rect x="52" y="10" width="8" height="52" rx="3" fill="#e8b923" transform="rotate(-1 56 36)"/>
        <rect x="64" y="16" width="8" height="48" rx="3" fill="#f2c879" transform="rotate(5 68 40)"/>
        <rect x="74" y="24" width="8" height="42" rx="3" fill="#e8b923" transform="rotate(11 78 45)"/>
    </svg>''',
    "maggi-pasta": '''<svg viewBox="0 0 120 120">
        <ellipse cx="60" cy="94" rx="46" ry="9" fill="#00000022"/>
        <path d="M14 60c0 22 20 38 46 38s46-16 46-38z" fill="#8a5a34"/>
        <ellipse cx="60" cy="60" rx="46" ry="16" fill="#c9822e"/>
        <path d="M28 56c6-6 10 6 16 0s10 6 16 0s10 6 16 0s10-6 16 0" stroke="#f2c879" stroke-width="4" fill="none" stroke-linecap="round"/>
        <circle cx="40" cy="52" r="3" fill="#c0392b"/><circle cx="66" cy="66" r="3" fill="#c0392b"/><circle cx="80" cy="54" r="3" fill="#3f8f5f"/>
    </svg>''',
    "south": '''<svg viewBox="0 0 120 120">
        <path d="M10 92c14-10 86-10 100 0l-6 8c-16-8-72-8-88 0z" fill="#3f8f5f"/>
        <ellipse cx="42" cy="78" rx="19" ry="13" fill="#f7f2e8"/>
        <ellipse cx="76" cy="78" rx="19" ry="13" fill="#f7f2e8"/>
        <ellipse cx="59" cy="66" rx="19" ry="13" fill="#fbf7ee"/>
        <circle cx="94" cy="86" r="7" fill="#c0392b"/>
    </svg>''',
    "drinks": '''<svg viewBox="0 0 120 120">
        <ellipse cx="60" cy="104" rx="30" ry="6" fill="#00000022"/>
        <path d="M38 30h44l-7 68a6 6 0 01-6 5H51a6 6 0 01-6-5z" fill="#c98f5c"/>
        <path d="M38 30h44l-2 16H40z" fill="#e8c078"/>
        <path d="M36 28h48v6H36z" fill="#f4e4c8"/>
        <circle cx="60" cy="24" r="7" fill="#c0392b"/>
        <rect x="66" y="4" width="5" height="26" rx="2.5" fill="#e8b923" transform="rotate(18 68 17)"/>
    </svg>''',
}


def _hash(s):
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h


def _wikimedia_url(filename, width=700):
    from urllib.parse import quote
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(filename)}?width={width}"


@register.simple_tag
def dish_photo(food_item, height=None):
    """Renders the full dish-photo block for a FoodItem (model instance)."""
    group = food_item.category.slug
    art = GROUP_ART.get(group, GROUP_ART["snacks"])
    style = f' style="height:{height}"' if height else ""
    ribbon = f'<span class="ribbon {food_item.tag}">{TAG_LABEL.get(food_item.tag, "")}</span>' if food_item.tag else ""

    uploaded = food_item.primary_image
    if uploaded:
        photo_img = (f'<img class="real-photo" src="{uploaded.image.url}" '
                     f'alt="{escape(food_item.name)}" loading="lazy" decoding="async">')
    else:
        override = ITEM_PHOTO_OVERRIDE.get(food_item.slug)
        pool = GROUP_PHOTO_POOL.get(group)
        filename = override or (pool[_hash(food_item.subcategory) % len(pool)] if pool else None)
        photo_img = (
            f'<img class="real-photo" src="{_wikimedia_url(filename)}" alt="{escape(food_item.name)}" '
            f'loading="lazy" decoding="async" onerror="this.style.display=\'none\'">'
        ) if filename else ""

    html = f'<div class="dish-photo dp-{group}"{style} role="img" aria-label="{escape(food_item.name)}">{art}{photo_img}{ribbon}</div>'
    return mark_safe(html)


@register.simple_tag
def cat_photo(category_slug, subcategory_name, height=None):
    """One representative photo for a whole sub-category section (menu/category showcase)."""
    art = GROUP_ART.get(category_slug, GROUP_ART["snacks"])
    style = f' style="height:{height}"' if height else ""
    pool = GROUP_PHOTO_POOL.get(category_slug)
    filename = pool[_hash(subcategory_name) % len(pool)] if pool else None
    photo_img = (
        f'<img class="real-photo" src="{_wikimedia_url(filename)}" alt="{escape(subcategory_name)}" '
        f'loading="lazy" decoding="async" onerror="this.style.display=\'none\'">'
    ) if filename else ""
    html = f'<div class="dish-photo dp-{category_slug}"{style} role="img" aria-label="{escape(subcategory_name)}">{art}{photo_img}</div>'
    return mark_safe(html)


@register.simple_tag
def cat_icon(category_slug):
    return mark_safe(GROUP_ART.get(category_slug, GROUP_ART["snacks"]))


@register.simple_tag
def veg_dot(is_veg):
    cls = "" if is_veg else " nonveg"
    label = "Veg" if is_veg else "Non-Veg"
    return mark_safe(f'<span class="veg-dot{cls}" title="{label}"></span>')


@register.filter
def price_label(food_item):
    if food_item.has_sizes:
        cheapest = food_item.sizes.order_by("price").first()
        return f"From ₹{cheapest.price:.0f}"
    return f"₹{food_item.price:.0f}" if food_item.price is not None else "—"
