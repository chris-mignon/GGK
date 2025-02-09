from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, Restaurant, MenuItem, Order, OrderItem
from flask_login import login_required, current_user

customer_bp = Blueprint('customer', __name__, template_folder='../templates/customer')

@customer_bp.route('/')
def restaurants():
    """List all restaurants."""
    restaurants = Restaurant.query.all()
    return render_template('customer/restaurants.html', restaurants=restaurants)

@customer_bp.route('/menu/<int:restaurant_id>')
def view_menu(restaurant_id):
    """View menu items for a specific restaurant."""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('customer/view_menu.html', restaurant=restaurant, menu_items=menu_items)

@customer_bp.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    """View and manage items in the cart."""
    if 'cart' not in session:
        session['cart'] = []

    if request.method == 'POST':
        menu_item_id = int(request.form['menu_item_id'])
        quantity = int(request.form['quantity'])
        session['cart'].append({'menu_item_id': menu_item_id, 'quantity': quantity})
        session.modified = True
        flash('Item added to cart!', 'success')
        return redirect(url_for('customer.cart'))

    cart_items = []
    total_price = 0
    for item in session.get('cart', []):
        menu_item = MenuItem.query.get(item['menu_item_id'])
        if menu_item:
            cart_items.append({
                'name': menu_item.name,
                'price': menu_item.price,
                'quantity': item['quantity'],
                'total': menu_item.price * item['quantity']
            })
            total_price += menu_item.price * item['quantity']

    return render_template('customer/cart.html', cart_items=cart_items, total_price=total_price)

@customer_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """Checkout and place an order."""
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('customer.cart'))

    # Create a new order
    total_price = 0
    new_order = Order(customer_id=current_user.id, status='Pending', total_price=0)
    db.session.add(new_order)
    db.session.flush()  # Get order ID before committing

    for item in session['cart']:
        menu_item = MenuItem.query.get(item['menu_item_id'])
        if menu_item:
            total_price += menu_item.price * item['quantity']
            order_item = OrderItem(order_id=new_order.id, menu_item_id=menu_item.id, quantity=item['quantity'])
            db.session.add(order_item)

    new_order.total_price = total_price
    db.session.commit()

    # Clear the cart
    session['cart'] = []
    session.modified = True

    flash('Order placed successfully!', 'success')
    return redirect(url_for('customer.restaurants'))


stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

@customer_bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    """Stripe payment page."""
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('customer.cart'))

    # Calculate total price
    total_price = 0
    for item in session['cart']:
        menu_item = MenuItem.query.get(item['menu_item_id'])
        if menu_item:
            total_price += menu_item.price * item['quantity']

    if request.method == 'POST':
        # Create Stripe charge
        try:
            stripe.Charge.create(
                amount=int(total_price * 100),  # Stripe expects amount in cents
                currency='usd',
                description='Food Order Payment',
                source=request.form['stripeToken']
            )
            flash('Payment successful!', 'success')
            return redirect(url_for('customer.checkout'))
        except stripe.error.StripeError as e:
            flash(f'Payment error: {e.user_message}', 'danger')
            return redirect(url_for('customer.payment'))

    return render_template('customer/payment.html', total_price=total_price)