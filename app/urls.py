from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('',            views.home,         name='home'),
    path('login/',      views.login_view,   name='login'),
    path('signup/',     views.signup_view,  name='signup'),
    path('logout/',     views.logout_view,  name='logout'),

    # Products
    path('products/',                   views.product_list,   name='product_list'),
    path('products/<int:pk>/',          views.product_detail, name='product_detail'),

    # Cart
    path('cart/',                           views.cart_view,        name='cart'),
    path('cart/add/<int:pk>/',              views.add_to_cart,      name='add_to_cart'),
    path('cart/remove/<int:item_id>/',      views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/',      views.update_cart,      name='update_cart'),
    path('wishlist/toggle/<int:pk>/',       views.toggle_wishlist,  name='toggle_wishlist'),

    # Orders
    path('checkout/',                       views.checkout_view, name='checkout'),
    path('buy/<int:pk>/',                   views.buy_now,       name='buy_now'),
    path('order-success/<int:order_id>/',   views.order_success, name='order_success'),
    path('order/<int:order_id>/',           views.order_detail,  name='order_detail'),
    path('orders/',                         views.order_history, name='order_history'),

    # Feedback
    path('feedback/', views.feedback_view, name='feedback'),

    # Admin Dashboard
    path('admin-dashboard/',              views.admin_dashboard,  name='admin_dashboard'),
    path('admin-dashboard/products/',     views.admin_products,   name='admin_products'),
    path('admin-dashboard/products/<int:pk>/edit/', views.admin_edit_product, name='admin_edit_product'),
    path('admin-dashboard/categories/',   views.admin_categories, name='admin_categories'),
    path('admin-dashboard/orders/',       views.admin_orders,     name='admin_orders'),
    path('admin-dashboard/customers/',    views.admin_customers,  name='admin_customers'),
    path('admin-dashboard/feedback/',     views.admin_feedback,   name='admin_feedback'),
]
