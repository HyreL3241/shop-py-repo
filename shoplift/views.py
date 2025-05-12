from django.shortcuts import render
from django.http import HttpResponse
from .models import Product
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout

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
    return render(request, 'home.html')

def product_view(request):
    return render(request, 'products.html')