from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, FoodItem, Offer


def home(request):
    signature = (FoodItem.objects.filter(tag="bestseller", is_available=True)
                 .select_related("category").order_by("?")[:4])
    # try to diversify categories among the 4 signature picks
    seen, picks = set(), []
    for item in FoodItem.objects.filter(tag="bestseller", is_available=True).select_related("category"):
        if item.category_id in seen:
            continue
        seen.add(item.category_id)
        picks.append(item)
        if len(picks) == 4:
            break
    if not picks:
        picks = list(signature)

    popular = (FoodItem.objects.filter(is_available=True).exclude(tag="")
               .select_related("category")[:10])
    categories = Category.objects.all()
    gallery_items = list(FoodItem.objects.filter(is_available=True).order_by("?")[:10])
    about_dish = FoodItem.objects.filter(subcategory__icontains="Parantha Combo").first() \
        or FoodItem.objects.filter(category__slug="paranthas").first()

    return render(request, "menu/home.html", {
        "signature_items": picks,
        "popular_items": popular,
        "categories": categories,
        "gallery_items": gallery_items,
        "about_dish": about_dish,
    })


def menu_list(request):
    query = request.GET.get("q", "").strip()
    veg_only = request.GET.get("veg") == "1"
    group = request.GET.get("g", "")

    items = FoodItem.objects.filter(is_available=True).select_related("category").prefetch_related("sizes")
    if query:
        items = items.filter(Q(name__icontains=query) | Q(subcategory__icontains=query))
    if veg_only:
        items = items.filter(is_veg=True)
    if group:
        items = items.filter(category__slug=group)

    # group by subcategory, preserving category order then item sort_order
    sections = {}
    order = []
    for item in items.order_by("category__sort_order", "sort_order", "name"):
        key = (item.category.slug, item.subcategory)
        if key not in sections:
            sections[key] = {"category": item.category, "subcategory": item.subcategory, "items": []}
            order.append(key)
        sections[key]["items"].append(item)

    return render(request, "menu/menu.html", {
        "sections": [sections[k] for k in order],
        "categories": Category.objects.all(),
        "query": query,
        "veg_only": veg_only,
        "active_group": group,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    items = (FoodItem.objects.filter(category=category, is_available=True)
             .prefetch_related("sizes").order_by("sort_order", "name"))

    sections = {}
    order = []
    for item in items:
        key = item.subcategory
        if key not in sections:
            sections[key] = {"subcategory": key, "items": []}
            order.append(key)
        sections[key]["items"].append(item)

    return render(request, "menu/category.html", {
        "category": category,
        "sections": [sections[k] for k in order],
        "categories": Category.objects.all(),
    })


def food_detail(request, slug):
    item = get_object_or_404(
        FoodItem.objects.select_related("category").prefetch_related("sizes", "images"),
        slug=slug, is_available=True
    )
    related = (FoodItem.objects.filter(category=item.category, is_available=True)
               .exclude(id=item.id)[:4])
    return render(request, "menu/food_detail.html", {"item": item, "related": related})


def offers(request):
    active_offers = Offer.objects.filter(is_active=True)
    return render(request, "menu/offers.html", {"offers": active_offers})


def about(request):
    hero_dish = FoodItem.objects.filter(tag="bestseller", is_veg=False).first() \
        or FoodItem.objects.filter(tag="bestseller").first()
    return render(request, "menu/about.html", {"hero_dish": hero_dish})


def contact(request):
    return render(request, "menu/contact.html")

