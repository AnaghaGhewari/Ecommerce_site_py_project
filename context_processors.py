"""
store/context_processors.py — Custom context processors.

Context processors are functions that run for EVERY request and inject
variables into every template. We use this to show the cart item count
in the navbar badge without repeating the logic in every view.
"""


def cart_count(request):
    """
    Returns the total number of items in the session cart.
    Available in templates as {{ cart_count }}.
    """
    cart = request.session.get('cart', {})
    count = sum(item['quantity'] for item in cart.values())
    return {'cart_count': count}
