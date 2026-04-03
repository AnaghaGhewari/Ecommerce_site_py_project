"""
store/views.py — All function-based views for the store.

Views handle the logic between URLs and templates:
  1. Receive an HTTP request
  2. Process data (query DB, update cart, etc.)
  3. Return an HTTP response (rendered template or redirect)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal

from .models import Product, Category, Order, OrderItem
from .forms import RegisterForm, CheckoutForm


# ═══════════════════════════════════════════════════════════════════════════
# HOME / PRODUCT LISTING
# ═══════════════════════════════════════════════════════════════════════════

def home(request):
    """
    Home page — shows all products with search and category filtering.

    Query params:
      ?q=<search term>     — filter by name/description
      ?category=<slug>     — filter by category
    """
    products = Product.objects.filter(in_stock=True)
    categories = Category.objects.all()

    # --- Search filtering ---
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # --- Category filtering ---
    category_slug = request.GET.get('category', '')
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'active_category': active_category,
    }
    return render(request, 'store/home.html', context)


# ═══════════════════════════════════════════════════════════════════════════
# PRODUCT DETAIL
# ═══════════════════════════════════════════════════════════════════════════

def product_detail(request, slug):
    """
    Show a single product's full details.
    Uses slug for SEO-friendly URLs (e.g., /product/wireless-mouse/).
    """
    product = get_object_or_404(Product, slug=slug)
    # Get related products from the same category (exclude current)
    related_products = Product.objects.filter(
        category=product.category, in_stock=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


# ═══════════════════════════════════════════════════════════════════════════
# CART OPERATIONS — stored in request.session['cart']
#
# Cart structure:  { "product_id": {"quantity": N, "price": "19.99"}, ... }
# We store price as string because Decimal isn't JSON-serializable.
# ═══════════════════════════════════════════════════════════════════════════

def add_to_cart(request, product_id):
    """Add a product to the session cart (or increment quantity)."""
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    product_id_str = str(product_id)  # Session keys must be strings

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'quantity': 1,
            'price': str(product.price),
        }

    request.session['cart'] = cart
    messages.success(request, f'"{product.name}" added to cart!')
    return redirect('cart')


def remove_from_cart(request, product_id):
    """Remove a product entirely from the session cart."""
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        messages.success(request, 'Item removed from cart.')

    return redirect('cart')


def update_cart(request, product_id):
    """
    Update the quantity of a product in the cart.
    Expects a POST with 'quantity' field.
    """
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        quantity = int(request.POST.get('quantity', 1))

        if product_id_str in cart:
            if quantity > 0:
                cart[product_id_str]['quantity'] = quantity
            else:
                del cart[product_id_str]  # Remove if quantity is 0

            request.session['cart'] = cart

    return redirect('cart')


def cart_view(request):
    """
    Display the shopping cart with all items and totals.
    Fetches fresh product data from DB (in case price/name changed).
    """
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')

    for product_id_str, item_data in cart.items():
        try:
            product = Product.objects.get(id=int(product_id_str))
            quantity = item_data['quantity']
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            continue  # Skip products that no longer exist

    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/cart.html', context)


# ═══════════════════════════════════════════════════════════════════════════
# CHECKOUT & ORDERS
# ═══════════════════════════════════════════════════════════════════════════

@login_required
def checkout(request):
    """
    Checkout page — shows order summary and shipping form.
    On POST: creates Order + OrderItems, clears cart, redirects to success.
    """
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('home')

    # Build cart items for display (same logic as cart_view)
    cart_items = []
    total = Decimal('0.00')
    for product_id_str, item_data in cart.items():
        try:
            product = Product.objects.get(id=int(product_id_str))
            quantity = item_data['quantity']
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            continue

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # --- Create the Order ---
            order = Order.objects.create(
                user=request.user,
                total_price=total,
                is_completed=True,
                full_name=form.cleaned_data['full_name'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                phone=form.cleaned_data['phone'],
            )
            # --- Create OrderItems for each cart item ---
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price,
                )
            # --- Clear the cart ---
            request.session['cart'] = {}
            messages.success(request, 'Order placed successfully!')
            return redirect('order_success', order_id=order.id)
    else:
        form = CheckoutForm()

    context = {
        'cart_items': cart_items,
        'total': total,
        'form': form,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_success(request, order_id):
    """Order confirmation page, shown after successful checkout."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def my_orders(request):
    """Show all past orders for the logged-in user."""
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/my_orders.html', {'orders': orders})


# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════

def register_view(request):
    """User registration — creates a new account and logs them in."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    """User login — authenticates and starts a session."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect to 'next' param if present (e.g., /checkout/)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'store/login.html')


def logout_view(request):
    """Log the user out and redirect to home."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')
