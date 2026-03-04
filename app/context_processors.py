import logging
from django.core.cache import cache
from django.db import connection
from django.db.utils import OperationalError
from .models import Category, Cart

logger = logging.getLogger(__name__)

def nav_categories(request):
    """
    Provide navigation categories and cart count to all templates.
    Uses caching to prevent database query on every request.
    """
    cart_count = 0
    nav_categories_list = []
    
    try:
        # Try to get categories from cache (2 hour TTL)
        cache_key = 'nav_categories'
        nav_categories_list = cache.get(cache_key)
        
        if nav_categories_list is None:
            # Only query database if not in cache
            try:
                nav_categories_list = list(Category.objects.all().values('id', 'name'))
                cache.set(cache_key, nav_categories_list, 60 * 60 * 2)  # Cache for 2 hours
                logger.debug(f"Loaded {len(nav_categories_list)} categories from database")
            except OperationalError as e:
                logger.error(f"Database connection error while fetching categories: {e}")
                nav_categories_list = [{'id': 0, 'name': 'Categories'}]
        
        # Get cart count only for authenticated non-admin users
        if request.user.is_authenticated and not request.user.is_admin:
            try:
                cart = Cart.objects.get(user=request.user)
                cart_count = cart.item_count()
            except Cart.DoesNotExist:
                cart_count = 0
            except Exception as e:
                logger.warning(f"Error fetching cart count for {request.user.username}: {e}")
                cart_count = 0
    
    except Exception as e:
        logger.error(f"Unexpected error in nav_categories context processor: {e}")
        nav_categories_list = []
        cart_count = 0
    
    return {
        'nav_categories': nav_categories_list,
        'cart_count': cart_count,
    }

