from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.home, name='home'),
    path('featured/', views.featured_products, name='featured-products'),
    path('login/', views.login_view, name='login'),  # Ensure this matches
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),  # Ensure this matches
    path('search/', views.search_view, name='search'),  # Ensure this matches
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('receipt/<int:order_id>/', views.receipt, name='receipt'),
    path('search/', views.search_view, name='search'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('load-more-products/', views.load_more_products, name='load_more_products'),
]