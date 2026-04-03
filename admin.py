"""
store/admin.py — Admin panel configuration.

Registers all models so you can manage products, categories,
and orders from Django's built-in admin interface at /admin/.
"""

from django.contrib import admin
from .models import Category, Product, Order, OrderItem


# ---------------------------------------------------------------------------
# Category Admin
# ---------------------------------------------------------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # Auto-fill slug from name


# ---------------------------------------------------------------------------
# Product Admin
# ---------------------------------------------------------------------------

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'in_stock', 'created_at']
    list_filter = ['category', 'in_stock', 'created_at']
    list_editable = ['price', 'in_stock']  # Edit directly in list view
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


# ---------------------------------------------------------------------------
# Order Admin — with inline OrderItems
# ---------------------------------------------------------------------------

class OrderItemInline(admin.TabularInline):
    """Show order items directly inside the Order admin page."""
    model = OrderItem
    extra = 0  # Don't show empty extra rows
    readonly_fields = ['product', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'created_at']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
