from flask import Blueprint, render_template, redirect, url_for, flash
from app.models import db, Order
from flask_login import login_required, current_user

delivery_bp = Blueprint('delivery', __name__, template_folder='../templates/delivery')

@delivery_bp.route('/')
@login_required
def deliveries():
    """View all pending deliveries."""
    if current_user.role != 'delivery_agent':
        flash('Access denied!', 'danger')
        return redirect(url_for('customer.restaurants'))

    orders = Order.query.filter_by(status='Pending').all()
    return render_template('delivery/deliveries.html', orders=orders)

@delivery_bp.route('/deliver/<int:order_id>')
@login_required
def mark_as_delivered(order_id):
    """Mark an order as delivered."""
    if current_user.role != 'delivery_agent':
        flash('Access denied!', 'danger')
        return redirect(url_for('customer.restaurants'))

    order = Order.query.get_or_404(order_id)
    order.status = 'Delivered'
    db.session.commit()
    flash('Order marked as delivered!', 'success')
    return redirect(url_for('delivery.deliveries'))