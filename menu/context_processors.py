from .models import Category
from orders.cart import Cart


def site_globals(request):
    return {
        "nav_categories": Category.objects.all(),
        "cart_count": len(Cart(request)),
    }
