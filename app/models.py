from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [('user', 'User'), ('admin', 'Admin')]
    role    = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone   = models.CharField(max_length=20, blank=True)
    avatar  = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_blocked = models.BooleanField(default=False)

    @property
    def is_admin(self):
        return self.role == 'admin'


class Category(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    SIZE_CHOICES = [('XS','XS'),('S','S'),('M','M'),('L','L'),('XL','XL'),('XXL','XXL')]
    name        = models.CharField(max_length=200)
    description = models.TextField()
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    old_price   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category    = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image       = models.ImageField(upload_to='products/')
    image2      = models.ImageField(upload_to='products/', blank=True, null=True)
    image3      = models.ImageField(upload_to='products/', blank=True, null=True)
    sizes       = models.CharField(max_length=100, default='XS,S,M,L,XL')
    stock       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    badge       = models.CharField(max_length=50, blank=True)  # NEW, SALE, etc.
    rating      = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    review_count = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0

    def sizes_list(self):
        return [s.strip() for s in self.sizes.split(',')]


class Cart(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def item_count(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    size     = models.CharField(max_length=10, default='M')
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.price * self.quantity


class Address(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    address1   = models.CharField(max_length=255)
    address2   = models.CharField(max_length=255, blank=True)
    city       = models.CharField(max_length=100)
    zip_code   = models.CharField(max_length=20)
    country    = models.CharField(max_length=100, default='India')
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.city}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending',   'Pending'),
        ('Processing','Processing'),
        ('Shipped',   'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [('COD','Cash on Delivery'),('UPI','UPI/QR'),('Card','Card Payment')]

    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address        = models.TextField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2)
    discount       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} — {self.user.username}"


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    size     = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField()
    price    = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity


class Feedback(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE)
    product   = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    order     = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    headline  = models.CharField(max_length=200, blank=True)
    message   = models.TextField()
    rating    = models.IntegerField(default=5)
    reply     = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    is_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} — {self.rating}★"


class Wishlist(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
