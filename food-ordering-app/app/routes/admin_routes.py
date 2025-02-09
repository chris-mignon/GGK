from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Restaurant, MenuItem, Order

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

@admin_bp.route('/')
def dashboard():
    """Admin dashboard to manage restaurants and orders."""
    restaurants = Restaurant.query.all()
    orders = Order.query.all()
    return render_template('admin/dashboard.html', restaurants=restaurants, orders=orders)

@admin_bp.route('/restaurant/add', methods=['GET', 'POST'])
def add_restaurant():
    """Add a new restaurant."""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_restaurant = Restaurant(name=name, description=description)
        db.session.add(new_restaurant)
        db.session.commit()
        flash('Restaurant added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_restaurant.html')

@admin_bp.route('/menu/<int:restaurant_id>', methods=['GET', 'POST'])
def manage_menu(restaurant_id):
    """Manage menu items for a specific restaurant."""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        new_item = MenuItem(name=name, price=price, restaurant_id=restaurant_id)
        db.session.add(new_item)
        db.session.commit()
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('admin.manage_menu', restaurant_id=restaurant_id))
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('admin/manage_menu.html', restaurant=restaurant, menu_items=menu_items)