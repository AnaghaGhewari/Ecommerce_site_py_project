"""
store/models.py — Database models for the e-commerce store.

Models:
  - Category  : Product categories (Electronics, Clothing, etc.)
  - Product   : Items for sale
  - Order     : A completed purchase by a user
  - OrderItem : Individual line-items inside an Order
"""

from django.db import models
from django.contrib.auth.models import User


# ---------------------------------------------------------------------------
# Category — groups products (e.g. "Electronics", "Books")
# ---------------------------------------------------------------------------

class Category(models.Model):
    """
    A product category.
    Each product belongs to exactly one category.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of the name")

    class Meta:
        verbose_name_plural = "Categories"  # Fix default "Categorys" in admin
        ordering = ['name']

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Product — the items customers can buy
# ---------------------------------------------------------------------------

class Product(models.Model):
    """
    A product in the store catalog.
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,       # Delete products if category is deleted
        related_name='products',         # category.products.all()
    )
    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of the name")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to='products/',           # Saved in MEDIA_ROOT/products/
        blank=True,
        null=True,
    )
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']       # Newest products first

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Order — a completed purchase
# ---------------------------------------------------------------------------

class Order(models.Model):
    """
    Represents a completed checkout.
    Links to the user who placed the order and tracks status.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',           # user.orders.all()
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Shipping details (simple text fields for the simulation)
    full_name = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


# ---------------------------------------------------------------------------
# OrderItem — a single product line inside an Order
# ---------------------------------------------------------------------------

class OrderItem(models.Model):
    """
    One row in an order — stores the product, the quantity,
    and the price at the time of purchase (in case the product
    price changes later).
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',            # order.items.all()
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,       # Keep order record even if product deleted
        null=True,
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name if self.product else 'Deleted product'}"

    def get_total(self):
        """Total cost for this line item."""
        return self.quantity * self.price
