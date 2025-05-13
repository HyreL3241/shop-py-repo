from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Category
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
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
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'authentication/register.html', {'error': 'Passwords do not match'})

        try:
            if User.objects.filter(username=username).exists():
                return render(request, 'authentication/register.html', {'error': 'Username already exists'})
            
            user = User.objects.create_user(username=username, password=password)
            user.save()
            return redirect('login')  # Redirect to login page after successful registration
        except Exception as e:
            return render(request, 'authentication/register.html', {'error': str(e)})

    return render(request, 'authentication/register.html')

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if user is not authenticated

    return render(request, 'profile.html', {'user': request.user})

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the home page after logout

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def search_view(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query)
    return render(request, 'product_list.html', {'products': products, 'query': query})

def home(request):
    import_products_from_csv()
    categories = Category.objects.all()
    return render(request, 'home.html', {'categories': categories})

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
    products = Product.objects.filter(rating__gte=4.5).values('name', 'category__name', 'image_url', 'price', 'rating')  # Fetch all except Description, Available Sizes, Available Colors
    return render(request, 'featured.html', {'products': products})
