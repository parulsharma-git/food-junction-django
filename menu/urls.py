from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.menu_list, name="menu"),
    path("category/<slug:slug>/", views.category_detail, name="category"),
    path("food/<slug:slug>/", views.food_detail, name="food_detail"),
    path("offers/", views.offers, name="offers"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]
