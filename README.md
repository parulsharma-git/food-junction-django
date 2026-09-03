# Food Junction — Django Full-Stack Site

Your original frontend design (dark charcoal/gold theme, hero, menu layout,
cart, checkout, animations) converted into a real Django + SQLite website.
The owner can now manage everything — menu items, prices, photos, offers,
and incoming orders — from the Django Admin, with no code changes needed.

---

## 1. How to run it locally

```bash
# from inside the foodjunction_django folder
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

python3 manage.py migrate         # sets up the database tables
python3 manage.py runserver
```

Then open: **http://127.0.0.1:8000/**

The database (`db.sqlite3`) that ships in this zip is **already seeded**
with all 140 menu items, 10 categories, and 2 starter offer codes, and
already has an admin account created (see below) — so it works immediately,
no extra setup required.

If you ever want to reset/reseed the menu from scratch:
```bash
python3 manage.py seed_menu --reset
```

---

## 2. Django Admin

URL: **http://127.0.0.1:8000/admin/**

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `FoodJunction@2026` |

**Change this password before handing the site to the owner** — either in
the Admin under "Change password" (top right after logging in), or:
```bash
python3 manage.py changepassword admin
```

To create additional staff logins for the owner or her staff:
```bash
python3 manage.py createsuperuser
```

### What the owner can do in Admin, without touching code:
- **Menu → Food items**: add/edit/delete dishes, change name/description/price,
  mark Veg/Non-veg, set a tag (Bestseller/Spicy/New), toggle **Is available**
  on/off (instantly hides it from the live site), upload one or more real
  photos per dish (first upload becomes the primary photo shown on the site —
  if no photo is uploaded, the site automatically falls back to a curated
  real photo, then to a drawn illustration, so nothing ever looks broken).
- **Menu → Food items → a pizza-type item**: add Size/Price rows inline
  (e.g. 8" / 10") instead of a single price.
- **Menu → Categories**: rename categories, change their order, edit taglines.
- **Menu → Offers**: add/edit/deactivate promo codes and their discount %.
- **Orders → Orders**: see every incoming order — customer name, phone,
  address, items ordered, quantities, total, payment method — and change
  status through Pending → Confirmed → Preparing → Out for Delivery →
  Delivered / Cancelled from a dropdown.

---

## 3. Project structure

```
foodjunction_django/
├── manage.py
├── requirements.txt
├── db.sqlite3                  # pre-seeded SQLite database
├── foodjunction/                # project settings & URL root
│   ├── settings.py
│   └── urls.py
├── menu/                        # categories, food items, offers
│   ├── models.py
│   ├── admin.py
│   ├── views.py
│   ├── urls.py
│   ├── templatetags/menu_extras.py   # dish photo/illustration rendering
│   ├── management/commands/seed_menu.py
│   └── fixtures/seed_data.json       # original menu data, converted from data.js
├── orders/                      # cart, checkout, orders
│   ├── models.py
│   ├── admin.py
│   ├── views.py
│   ├── cart.py                  # session-based cart logic
│   └── urls.py
├── templates/
│   ├── base.html                 # nav + footer (server-rendered)
│   ├── menu/                     # home, menu, category, food_detail, offers, about, contact
│   └── orders/                   # cart, checkout, order_success
├── static/
│   ├── css/style.css             # your original design, unchanged (+ mobile cart fix)
│   └── js/main.js                # trimmed: nav/scroll/reveal/toast only
└── media/food_images/            # owner-uploaded dish photos land here
```

---

## 4. What's completed

- ✅ Django + SQLite backend, all data-driven (no hardcoded JS menu data anymore)
- ✅ Models: Category, FoodItem, FoodItemSize, FoodItemImage, Offer, Order, OrderItem
- ✅ Full Django Admin for menu, availability, photo uploads, offers, and order management
- ✅ Original frontend design fully preserved (same CSS, same layout, same animations)
- ✅ Session-based cart: multiple different items, qty +/-, remove, promo codes, persists
  across page navigation without localStorage
- ✅ "Add to Cart" vs "Buy Now" (Buy Now skips the cart and goes straight to checkout)
- ✅ Checkout creates a real `Order` + `OrderItem` records; generates an order ID (e.g. `FJ807826`)
- ✅ Order success page with order ID and delivery tracker UI
- ✅ Payment method selection (COD / Online) — UI + data model ready for a real
  gateway later, no gateway wired up yet (see below)
- ✅ **Mobile cart bug fixed**: the food image no longer overlaps the name/price/qty —
  rebuilt with a flexbox layout that cannot overlap, verified at 320px, 375px, 390px, 430px
- ✅ Navbar/hero overlap checked — the "Welcome to Food Junction" heading has correct
  clearance under the fixed navbar on mobile and desktop
- ✅ Food images: real photos matching each dish's category, with a same-category rotation
  so neighbouring dishes don't repeat the same photo; owner-uploaded photos always take priority
- ✅ Tested: home, menu, category, food details, add to cart, multiple items in cart,
  quantity changes, remove item, buy now, checkout, COD order creation, order visible
  in Admin, food item add/edit/availability toggle, image upload via Admin, mobile
  layout at required widths, no console errors on any page, internal links crawled (200s)

## 5. What's intentionally NOT implemented yet

- ❌ **Real online payment gateway** (e.g. Razorpay). The "Online Payment" option
  exists in the UI and is saved on the Order (`payment_method`, `is_paid` fields),
  but no real transaction is processed — this was explicitly out of scope for
  this demo. To add Razorpay later: create the order as `is_paid=False`, redirect
  to Razorpay Checkout with the `total` amount, then mark `is_paid=True` in a
  webhook/callback view before showing the success page.
- ❌ SMS/email order notifications to the owner or customer (not requested).
- ❌ Production deployment config (this uses Django's built-in dev server and
  `DEBUG=True`, correct for local demo use only — not for a public server).
