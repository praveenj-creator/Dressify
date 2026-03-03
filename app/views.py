from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import QueryDict
from django.urls import resolve
from django.urls.exceptions import Resolver404
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem, Address, Feedback, Wishlist
from .forms import SignupForm, LoginForm, AddressForm, FeedbackForm, ProductForm, CategoryForm
import decimal


def is_safe_url(url, allowed_hosts=None):
    """Verify that URL is safe to redirect to (internal only, no external redirects)"""
    if not url:
        return False
    # Must start with /
    if not url.startswith('/'):
        return False
    # Must not start with //
    if url.startswith('//'):
        return False
    # Try to resolve the URL to ensure it's valid
    try:
        resolve(url.split('?')[0])  # split query string
        return True
    except Resolver404:
        return False


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        if not request.user.is_admin:
            messages.error(request, 'Access denied.')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/admin-dashboard/' if request.user.is_admin else '/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # STEP 1: Ensure admin account exists BEFORE authenticate() is called
        if username == 'admin':
            if not User.objects.filter(username='admin').exists():
                u = User(username='admin', role='admin',
                         first_name='Admin', last_name='User',
                         is_staff=False, is_superuser=False)
                u.set_password('admin')
                u.save()

        # STEP 2: Now authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_blocked:
                return render(request, 'login.html',
                    {'error': 'Account blocked. Contact support.'})
            login(request, user)
            if user.is_admin:
                return redirect('/admin-dashboard/')
            # Validate the next parameter to prevent open redirects
            next_url = request.GET.get('next', '/')
            if is_safe_url(next_url):
                return redirect(next_url)
            return redirect('/')
        else:
            return render(request, 'login.html',
                {'error': 'Invalid username or password. Admin default: admin / admin'})

    return render(request, 'login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user'
            user.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name or user.username}!')
            return redirect('/')
        return render(request, 'signup.html', {'form': form, 'errors': form.errors})
    return render(request, 'signup.html', {'form': SignupForm()})


def logout_view(request):
    logout(request)
    return redirect('/login/')


def home(request):
    categories   = Category.objects.all()
    featured     = Product.objects.filter(is_active=True, is_featured=True)[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    return render(request, 'home.html', {
        'categories': categories, 'featured': featured, 'new_arrivals': new_arrivals,
    })


def product_list(request):
    products   = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    cat_id     = request.GET.get('category')
    q          = request.GET.get('q', '')
    min_price  = request.GET.get('min_price')
    max_price  = request.GET.get('max_price')
    sort       = request.GET.get('sort', 'newest')
    selected_cat = None
    if cat_id:
        products = products.filter(category_id=cat_id)
        selected_cat = Category.objects.filter(id=cat_id).first()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    sort_map = {'newest': '-created_at', 'price_low': 'price',
                'price_high': '-price', 'popular': '-review_count'}
    products = products.order_by(sort_map.get(sort, '-created_at'))

    # pagination
    paginator = Paginator(products, 12)  # show 12 products per page
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # preserve query parameters except page
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    qs = query_params.urlencode()

    return render(request, 'products.html', {
        'products': page_obj, 'categories': categories,
        'selected_cat': selected_cat, 'q': q, 'sort': sort,
        'page_obj': page_obj, 'paginator': paginator, 'is_paginated': page_obj.has_other_pages(),
        'querystring': qs,
    })


def product_detail(request, pk):
    product   = get_object_or_404(Product, pk=pk, is_active=True)
    related   = Product.objects.filter(category=product.category, is_active=True).exclude(pk=pk)[:4]
    feedbacks = Feedback.objects.filter(product=product).order_by('-created_at')[:10]
    in_wishlist = False
    if request.user.is_authenticated and not request.user.is_admin:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    return render(request, 'product_detail.html', {
        'product': product, 'related': related,
        'feedbacks': feedbacks, 'in_wishlist': in_wishlist,
    })


@login_required(login_url='/login/')
def cart_view(request):
    if request.user.is_admin:
        return redirect('/admin-dashboard/')
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items    = cart.items.select_related('product')
    subtotal = cart.total()
    discount = subtotal * decimal.Decimal('0.10') if subtotal > 500 else decimal.Decimal('0')
    total    = subtotal - discount
    return render(request, 'cart.html', {
        'cart': cart, 'items': items,
        'subtotal': subtotal, 'discount': discount, 'total': total,
    })


@login_required(login_url='/login/')
def add_to_cart(request, pk):
    if request.user.is_admin:
        return redirect('/admin-dashboard/')
    product = get_object_or_404(Product, pk=pk)
    size    = request.POST.get('size', 'M')
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, size=size)
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f'{product.name} added to cart!')
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/login/')
def remove_from_cart(request, item_id):
    CartItem.objects.filter(id=item_id, cart__user=request.user).delete()
    return redirect('/cart/')


@login_required(login_url='/login/')
def update_cart(request, item_id):
    qty  = int(request.POST.get('quantity', 1))
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if qty < 1:
        item.delete()
    else:
        item.quantity = qty
        item.save()
    return redirect('/cart/')


@login_required(login_url='/login/')
def toggle_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    w, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        w.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/login/')
def checkout_view(request):
    if request.user.is_admin:
        return redirect('/admin-dashboard/')
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        return redirect('/cart/')
    addresses = Address.objects.filter(user=request.user)
    addr_form = AddressForm()
    subtotal  = cart.total()
    discount  = subtotal * decimal.Decimal('0.10') if subtotal > 500 else decimal.Decimal('0')
    total     = subtotal - discount
    if request.method == 'POST':
        payment = request.POST.get('payment_method', 'COD')
        addr_id = request.POST.get('saved_address')
        if addr_id:
            addr     = get_object_or_404(Address, id=addr_id, user=request.user)
            addr_str = f"{addr.first_name} {addr.last_name}, {addr.address1}, {addr.city} {addr.zip_code}, {addr.country}"
        else:
            form = AddressForm(request.POST)
            if not form.is_valid():
                return render(request, 'checkout.html', {
                    'cart': cart, 'addresses': addresses, 'addr_form': form,
                    'subtotal': subtotal, 'discount': discount, 'total': total,
                    'items': cart.items.select_related('product'),
                })
            addr = form.save(commit=False)
            addr.user = request.user
            addr.save()
            addr_str = f"{addr.first_name} {addr.last_name}, {addr.address1}, {addr.city} {addr.zip_code}, {addr.country}"
        order = Order.objects.create(
            user=request.user, address=addr_str,
            payment_method=payment, total_amount=total, discount=discount,
        )
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order, product=item.product,
                size=item.size, quantity=item.quantity, price=item.product.price,
            )
        cart.items.all().delete()
        return redirect(f'/order-success/{order.id}/')
    return render(request, 'checkout.html', {
        'cart': cart, 'addresses': addresses, 'addr_form': addr_form,
        'subtotal': subtotal, 'discount': discount, 'total': total,
        'items': cart.items.select_related('product'),
    })


@login_required(login_url='/login/')
def buy_now(request, pk):
    if request.user.is_admin:
        return redirect('/admin-dashboard/')
    product = get_object_or_404(Product, pk=pk)
    size    = request.POST.get('size', 'M')
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    CartItem.objects.create(cart=cart, product=product, size=size, quantity=1)
    return redirect('/checkout/')


@login_required(login_url='/login/')
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})


@login_required(login_url='/login/')
def order_detail(request, order_id):
    """Display full details of a single order"""
    if request.user.is_admin:
        return redirect('/admin-dashboard/')
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.select_related('product')
    return render(request, 'order_detail.html', {'order': order, 'items': items})


@login_required(login_url='/login/')
def order_history(request):
    if request.user.is_admin:
        return redirect('/admin-dashboard/')
    status = request.GET.get('status', 'all')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    if status != 'all':
        orders = orders.filter(status=status)

    # pagination
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    qs = query_params.urlencode()

    return render(request, 'order_history.html', {
        'orders': page_obj, 'status': status,
        'page_obj': page_obj, 'paginator': paginator, 'is_paginated': page_obj.has_other_pages(),
        'querystring': qs,
    })


@login_required(login_url='/login/')
def feedback_view(request):
    if request.user.is_admin:
        return redirect('/admin-dashboard/')
    products = Product.objects.filter(is_active=True)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.user = request.user
            pid = request.POST.get('product_id')
            if pid:
                fb.product = Product.objects.filter(id=pid).first()
            fb.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('/feedback/')
    else:
        form = FeedbackForm()
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'feedback.html', {
        'form': form, 'feedbacks': feedbacks, 'products': products,
    })


# ══ ADMIN VIEWS ══════════════════════════════════════════════════════════════

@admin_required
def admin_dashboard(request):
    from django.db.models.functions import TruncMonth
    monthly = (Order.objects.exclude(status='Cancelled')
               .annotate(month=TruncMonth('created_at'))
               .values('month').annotate(total=Sum('total_amount')).order_by('month'))
    return render(request, 'admin/dashboard.html', {
        'total_users':    User.objects.filter(role='user').count(),
        'total_orders':   Order.objects.count(),
        'total_revenue':  Order.objects.exclude(status='Cancelled').aggregate(t=Sum('total_amount'))['t'] or 0,
        'pending_orders': Order.objects.filter(status='Pending').count(),
        'recent_orders':  Order.objects.select_related('user').order_by('-created_at')[:10],
        'monthly':        list(monthly),
        'active_tab':     'dashboard',
    })


@admin_required
def admin_products(request):
    all_products = Product.objects.select_related('category').order_by('-created_at')
    categories = Category.objects.all()
    form       = ProductForm()

    # pagination for admin listing
    paginator = Paginator(all_products, 15)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    products = page_obj
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product added!')
                return redirect('/admin-dashboard/products/')
        elif action == 'delete':
            Product.objects.filter(id=request.POST.get('product_id')).delete()
            messages.success(request, 'Product deleted.')
            return redirect('/admin-dashboard/products/')
    return render(request, 'admin/products.html', {
        'products': products, 'categories': categories, 'form': form,
        'active_tab': 'products',
        'total_products': paginator.count,
        'active_stock':   all_products.filter(stock__gt=0).count(),
        'out_of_stock':   all_products.filter(stock=0).count(),
        'page_obj': page_obj, 'paginator': paginator, 'is_paginated': page_obj.has_other_pages(),
    })


@admin_required
def admin_edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product updated!')
        return redirect('/admin-dashboard/products/')
    return render(request, 'admin/edit_product.html', {
        'form': form, 'product': product, 'active_tab': 'products',
    })


@admin_required
def admin_categories(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    form = CategoryForm()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = CategoryForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category added!')
                return redirect('/admin-dashboard/categories/')
        elif action == 'delete':
            Category.objects.filter(id=request.POST.get('cat_id')).delete()
            messages.success(request, 'Category deleted.')
            return redirect('/admin-dashboard/categories/')
    return render(request, 'admin/categories.html', {
        'categories': categories, 'form': form, 'active_tab': 'categories',
    })


@admin_required
def admin_orders(request):
    sf     = request.GET.get('status', '')
    orders = Order.objects.select_related('user').prefetch_related('items__product').order_by('-created_at')
    if sf:
        orders = orders.filter(status=sf)

    # pagination
    paginator = Paginator(orders, 20)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    orders = page_obj

    if request.method == 'POST':
        oid = request.POST.get('order_id')
        ns  = request.POST.get('status')
        if oid and ns:
            Order.objects.filter(id=oid).update(status=ns)
            messages.success(request, 'Order status updated.')
        return redirect('/admin-dashboard/orders/')
    return render(request, 'admin/orders.html', {
        'orders': orders, 'status_filter': sf,
        'active_tab': 'orders', 'status_choices': Order.STATUS_CHOICES,
        'page_obj': page_obj, 'paginator': paginator, 'is_paginated': page_obj.has_other_pages(),
    })


@admin_required
def admin_customers(request):
    q     = request.GET.get('q', '')
    users = User.objects.filter(role='user').order_by('-date_joined')
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))

    # pagination
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    users = page_obj

    # preserve q parameter for pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    qs = query_params.urlencode()
    if request.method == 'POST':
        uid    = request.POST.get('user_id')
        action = request.POST.get('action')
        u      = User.objects.filter(id=uid).first()
        if u:
            u.is_blocked = (action == 'block')
            u.save()
            messages.success(request, f'{u.username} {"blocked" if u.is_blocked else "unblocked"}.')
        return redirect('/admin-dashboard/customers/')
    return render(request, 'admin/customers.html', {
        'users': users, 'q': q, 'active_tab': 'customers',
        'total_users':   User.objects.filter(role='user').count(),
        'active_users':  User.objects.filter(role='user', is_blocked=False).count(),
        'blocked_users': User.objects.filter(role='user', is_blocked=True).count(),
        'page_obj': page_obj, 'paginator': paginator, 'is_paginated': page_obj.has_other_pages(),
        'qs': qs,
    })


@admin_required
def admin_feedback(request):
    tab       = request.GET.get('tab', 'all')
    feedbacks = Feedback.objects.select_related('user', 'product').order_by('-created_at')
    if tab == 'pending':
        feedbacks = feedbacks.filter(is_replied=False)
    elif tab == 'replied':
        feedbacks = feedbacks.filter(is_replied=True)

    # pagination
    paginator = Paginator(feedbacks, 15)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    feedbacks = page_obj
    if request.method == 'POST':
        fb_id = request.POST.get('feedback_id')
        reply = request.POST.get('reply', '')
        fb    = Feedback.objects.filter(id=fb_id).first()
        if fb and reply:
            fb.reply = reply
            fb.is_replied = True
            fb.replied_at = timezone.now()
            fb.save()
            messages.success(request, 'Reply sent!')
        return redirect('/admin-dashboard/feedback/')
    return render(request, 'admin/feedback.html', {
        'feedbacks':     feedbacks,
        'tab':           tab,
        'active_tab':    'feedback',
        'total_reviews': Feedback.objects.count(),
        'avg_rating':    round(Feedback.objects.aggregate(a=Avg('rating'))['a'] or 0, 1),
        'pending_count': Feedback.objects.filter(is_replied=False).count(),
        'page_obj': page_obj, 'paginator': paginator, 'is_paginated': page_obj.has_other_pages(),
    })
