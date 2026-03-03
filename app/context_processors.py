from .models import Category, Cart

def nav_categories(request):
    cart_count = 0
    if request.user.is_authenticated and not request.user.is_admin:
        try:
            cart_count = request.user.cart.item_count()
        except Exception:
            cart_count = 0
    return {
        'nav_categories': Category.objects.all(),
        'cart_count': cart_count,
    }
