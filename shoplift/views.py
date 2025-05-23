from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from .models import Product, CartItem, Wishlist, Order, OrderItem, Category
from math import floor

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'authentication/login.html', {'error': 'Invalid username or password'})
    return render(request, 'authentication/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'authentication/register.html', {'error': 'Passwords do not match'})
        if User.objects.filter(username=username).exists():
            return render(request, 'authentication/register.html', {'error': 'Username already exists'})
        if User.objects.filter(email=email).exists():
            return render(request, 'authentication/register.html', {'error': 'Email already in use'})

        try:
            User.objects.create_user(username=username, password=password, email=email)
            return redirect('login')
        except Exception as e:
            return render(request, 'authentication/register.html', {'error': str(e)})

    return render(request, 'authentication/register.html')

@login_required(login_url='/login/')
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

def logout_view(request):
    logout(request)
    return redirect('home')

def product_search(request):
    products = Product.objects.all()
    return render(request, 'product_search.html', {'products': products})

def search_view(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else []
    product_ids_in_cart = set()
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user).only('product_id')
        product_ids_in_cart = {item.product_id for item in cart_items}

    return render(request, 'product_search.html', {'products': products, 'query': query, 'product_ids_in_cart': product_ids_in_cart})

def home(request):
    categories = Category.objects.all()
    wishlist_product_ids = set()
    if request.user.is_authenticated:
        wishlist_product_ids = set(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))

    product_list = Product.objects.all()
    for product in product_list:
        product.rating_int = min(5, round(product.rating))

    paginator = Paginator(product_list, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'home.html', {
        'categories': categories,
        'page_obj': page_obj,
        'wishlist_product_ids': wishlist_product_ids,
    })

def load_more_products(request):
    paginator = Paginator(Product.objects.all(), 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_html = [
            render_to_string('partials/product_card.html', {'product': product}, request=request)
            for product in page_obj
        ]
        return JsonResponse({
            'products_html': products_html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None
        })
    return redirect('home')

def product_view(request):
    return render(request, 'products.html')

def featured_products(request):
    products = Product.objects.filter(rating__gte=4.5)
    return render(request, 'featured.html', {'products': products})

@login_required(login_url='/login/')
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product, defaults={'quantity': 1})
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_count = CartItem.objects.filter(user=request.user).count()
        return JsonResponse({
            'message': f'Added "{product.name}" to cart.',
            'cart_count': cart_count
        })
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required(login_url='/login/')
def remove_from_cart(request, cart_item_id):
    if request.method == 'POST':
        get_object_or_404(CartItem, id=cart_item_id, user=request.user).delete()
        return redirect('cart_view')

@login_required(login_url='/login/')
def cart_view(request):
    categories = Category.objects.all()
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'categories': categories
    })

@require_POST
@login_required
def update_cart(request):
    for key, value in request.POST.items():
        if key.startswith('quantities_'):
            try:
                cart_item_id = key.split('_')[1]
                cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
                quantity = int(value)
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
            except (ValueError, CartItem.DoesNotExist):
                continue
    return redirect('cart_view')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist_product_ids = set()
    product_in_cart = False

    if request.user.is_authenticated:
        wishlist_product_ids = set(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
        product_in_cart = CartItem.objects.filter(user=request.user, product=product).exists()

    return render(request, 'product_detail.html', {
        'product': product,
        'wishlist_product_ids': wishlist_product_ids,
        'product_in_cart': product_in_cart,
    })

@login_required(login_url='/login/')
@require_POST
def place_order(request):
    name = request.POST.get('name')
    contact = request.POST.get('contact')
    address = request.POST.get('address')
    payment_method = request.POST.get('payment_method')

    if not all([name, contact, address, payment_method]):
        return render(request, 'checkout.html', {'error': 'All fields are required.'})

    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return render(request, 'checkout.html', {'error': 'Your cart is empty.'})

    total_price = sum(item.quantity * item.product.price for item in cart_items)
    order = Order.objects.create(user=request.user, name=name, contact=contact,
                                 address=address, payment_method=payment_method,
                                 total_price=total_price)
    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product,
                                 quantity=item.quantity, price=item.product.price)
    cart_items.delete()
    return redirect('receipt', order_id=order.id)

@login_required(login_url='/login/')
def checkout(request):
    if request.method == 'POST':
        # Your place_order logic here (copy-paste)
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        if not all([name, contact, address, payment_method]):
            return render(request, 'checkout.html', {'error': 'All fields are required.'})

        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return render(request, 'checkout.html', {'error': 'Your cart is empty.'})

        total_price = sum(item.quantity * item.product.price for item in cart_items)
        order = Order.objects.create(user=request.user, name=name, contact=contact,
                                     address=address, payment_method=payment_method,
                                     total_price=total_price)
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product,
                                     quantity=item.quantity, price=item.product.price)
        cart_items.delete()
        return redirect('receipt', order_id=order.id)

    return render(request, 'checkout.html')

@login_required(login_url='/login/')
def receipt(request, order_id):
    categories = Category.objects.all()
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    total_price = sum(item.price * item.quantity for item in order_items)
    return render(request, 'order_receipt.html', {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
        'categories': categories
    })

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    cart_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'category_products.html', {
        'products': products,
        'category': category,
        'categories': categories,
        'cart_count': cart_count
    })

def collection_products(request, collection_slug):
    valid_collections = dict(Product.COLLECTION_CHOICES).keys()
    if collection_slug not in valid_collections:
        return redirect('home')
    products = Product.objects.filter(collection=collection_slug)
    categories = Category.objects.all()
    return render(request, 'collection_products.html', {
        'products': products,
        'collection_slug': collection_slug,
        'categories': categories
    })

def all_products(request):
    products = Product.objects.all()
    product_ids_in_cart = set()
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user).only('product_id')
        product_ids_in_cart = {item.product_id for item in cart_items}
    return render(request, 'all_products.html', {
        'products': products,
        'product_ids_in_cart': product_ids_in_cart,
    })

def about_us(request):
    return render(request, 'about_us.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            return redirect('change_password', username=user.username)
        return render(request, 'forgot_password.html', {'error': 'No user found with that email address'})
    return render(request, 'forgot_password.html')

def change_password_view(request, username):
    user = User.objects.filter(username=username).first()
    if not user:
        return redirect('forgot_password')
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if not new_password or not confirm_password:
            return render(request, 'change_password.html', {'username': username, 'error': 'Fill all fields'})
        if new_password != confirm_password:
            return render(request, 'change_password.html', {'username': username, 'error': 'Passwords do not match'})
        user.password = make_password(new_password)
        user.save()
        return redirect('login')
    return render(request, 'change_password.html', {'username': username})

@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist': wishlist})

@login_required
@require_POST
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'message': f'Added "{product.name}" to wishlist.',
            'product_id': product_id
        })

    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'message': f'Removed product {product_id} from wishlist.',
            'product_id': product_id
        })

    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))

@login_required(login_url='/login/')
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})

@login_required(login_url='/login/')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()  # via related_name='items' in OrderItem
    return render(request, 'order_detail.html', {'order': order, 'order_items': order_items})
