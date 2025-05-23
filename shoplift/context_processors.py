from .models import CartItem, Category

def cart_and_categories(request):
    cart_count = 0
    categories = Category.objects.all()[:6]

    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()

    return {
        'cart_count': cart_count,
        'categories': categories
    }