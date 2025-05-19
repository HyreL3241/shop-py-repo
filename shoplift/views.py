from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import csv


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page after login
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
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
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            return redirect('login')
        except Exception as e:
            return render(request, 'authentication/register.html', {'error': str(e)})

    return render(request, 'authentication/register.html')

@login_required(login_url='/login/')
def profile_view(request):
    user = request.user
    cart_count = CartItem.objects.filter(user=request.user).aggregate(total=models.Sum('quantity'))['total'] or 0

    return render(request, 'profile.html', {'user': user, 'cart_count': cart_count})

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the home page after logout

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def search_view(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else []
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).aggregate(total=models.Sum('quantity'))['total'] or 0

    return render(request, 'product_list.html', {'products': products, 'query': query, 'cart_count': cart_count})

def home(request):
    import_products_from_csv()
    categories = Category.objects.all()
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).aggregate(total=models.Sum('quantity'))['total'] or 0
    return render(request, 'home.html', {'categories': categories, 'cart_count': cart_count,})

def product_view(request):
    return render(request, 'products.html')

def import_products_from_csv():
    csv_path = r'C:\Users\hyrel\OneDrive\Desktop\shoplift\products.csv'

    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Get or create the category
                category_name = row.get("Category", "Uncategorized").strip()
                category, _ = Category.objects.get_or_create(name=category_name)

                # Create and save the product
                Product.objects.create(
                    name=row['Product Name'].strip(),
                    category=category,
                    image_url=row.get('Image URL', '').strip(),
                    price=float(row.get('Price (PHP)', 0)),
                    rating=float(row.get('Rating', 0)),
                    description=row.get('Description', '').strip(),
                    available_sizes=row.get('Available Sizes', '').strip(),
                    available_colors=row.get('Available Colors', '').strip()
                )

        return HttpResponse("Products imported successfully into SQLite database.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")

def featured_products(request):
    products = Product.objects.filter(rating__gte=4.5)
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).aggregate(total=models.Sum('quantity'))['total'] or 0

    return render(request, 'featured.html', {'products': products, 'cart_count': cart_count,})

@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': 1}
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()
        else:
            cart = request.session.get('cart', {})
            product_key = str(product_id)
            cart[product_key] = cart.get(product_key, 0) + 1
            request.session['cart'] = cart
            request.session.modified = True
        return redirect('cart_view')

@login_required(login_url='/login/')
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        product_key = str(product_id)
        if request.user.is_authenticated:
            product = get_object_or_404(Product, id=product_id)
            CartItem.objects.filter(user=request.user, product=product).delete()
        else:
            cart = request.session.get('cart', {})
            if product_key in cart:
                del cart[product_key]
                request.session['cart'] = cart
                request.session.modified = True
        return redirect('cart_view')

@login_required(login_url='/login/')
def cart_view(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        cart_count = CartItem.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
    else:
        session_cart = request.session.get('cart', {})
        product_ids = session_cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart_items = []
        total_price = 0
        for product in products:
            quantity = session_cart.get(str(product.id), 0)
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        cart_count = sum(session_cart.values())

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': cart_count,
    }
    return render(request, 'cart.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

@login_required(login_url='/login/')
@require_POST
def place_order(request):
    name = request.POST.get('name')
    contact = request.POST.get('contact')
    address = request.POST.get('address')
    payment_method = request.POST.get('payment_method')

    if not all([name, contact, address, payment_method]):
        return render(request, 'checkout.html', {
            'error': 'All fields are required.'
        })

    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return render(request, 'checkout.html', {
            'error': 'Your cart is empty.'
        })

    total_price = sum(item.quantity * item.product.price for item in cart_items)

    order = Order.objects.create(
        user=request.user,
        name=name,
        contact=contact,
        address=address,
        payment_method=payment_method,
        total_price=total_price
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    cart_items.delete()
    return redirect('receipt', order_id=order.id)

@login_required(login_url='/login/')
def checkout(request):
    cart_count = CartItem.objects.filter(user=request.user).aggregate(total=models.Sum('quantity'))['total'] or 0

    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        if not all([name, contact, address, payment_method]):
            return render(request, 'checkout.html', {'error': 'All fields are required.'})

        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return render(request, 'checkout.html', {'error': 'Your cart is empty.'})

        order = Order.objects.create(
            user=request.user,
            name=name,
            contact=contact,
            address=address,
            payment_method=payment_method,
            total_price=sum(item.subtotal for item in cart_items)
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        cart_items.delete()
        return redirect('receipt', order_id=order.id)
    
    return render(request, 'checkout.html', {'cart_count': cart_count,})

@login_required(login_url='/login/')
def receipt(request, order_id):
    cart_count = CartItem.objects.filter(user=request.user).aggregate(total=models.Sum('quantity'))['total'] or 0

    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    total_price = sum(item.price * item.quantity for item in order_items)

    context = {
        'cart_count': cart_count,
        'order': order,
        'order_items': order_items,
        'total_price': total_price
    }
    return render(request, 'order_receipt.html', context)