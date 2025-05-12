from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_view, name='product-view'),
    path('login/', views.login_view, name='login'),  # Ensure this matches
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),  # Ensure this matches
    path('logout/', views.logout_view, name='logout'),  # Ensure this matches
    path('search/', views.search_view, name='search'),  # Ensure this matches
]