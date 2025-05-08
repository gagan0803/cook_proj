from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.inventory import Inventory
from forms import InventoryForm
from config import Config
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/')
@login_required
def index():
    # Get all inventory items for the current user
    inventory_items = Inventory.get_by_user_id(current_user.id)
    
    # Get items that are expiring soon
    expiring_items = Inventory.get_expiring_items(
        current_user.id, 
        Config.INVENTORY_EXPIRY_WARNING_DAYS
    )
    
    # Get all categories
    categories = Config.INGREDIENT_CATEGORIES
    
    return render_template(
        'inventory/index.html', 
        inventory_items=inventory_items,
        expiring_items=expiring_items,
        categories=categories
    )

@inventory_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = InventoryForm()
    
    if form.validate_on_submit():
        # Create new inventory item
        item = Inventory.add_item(
            user_id=current_user.id,
            ingredient_name=form.ingredient_name.data,
            category=form.category.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            expiry_date=form.expiry_date.data
        )
        
        if item:
            flash('Ingredient added successfully!', 'success')
            return redirect(url_for('inventory.index'))
        else:
            flash('Error adding ingredient. Please try again.', 'danger')
    
    return render_template('inventory/add.html', form=form, title='Add Ingredient')

@inventory_bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    # Get inventory item
    item = Inventory.get_by_id(item_id)
    
    if not item or item.user_id != current_user.id:
        flash('Ingredient not found.', 'danger')
        return redirect(url_for('inventory.index'))
    
    form = InventoryForm(obj=item)
    
    if form.validate_on_submit():
        # Update inventory item
        updated_item = Inventory.update_item(
            item_id=item_id,
            ingredient_name=form.ingredient_name.data,
            category=form.category.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            expiry_date=form.expiry_date.data
        )
        
        if updated_item:
            flash('Ingredient updated successfully!', 'success')
            return redirect(url_for('inventory.index'))
        else:
            flash('Error updating ingredient. Please try again.', 'danger')
    
    return render_template('inventory/edit.html', form=form, item=item, title='Edit Ingredient')

@inventory_bp.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete(item_id):
    # Get inventory item
    item = Inventory.get_by_id(item_id)
    
    if not item or item.user_id != current_user.id:
        flash('Ingredient not found.', 'danger')
        return redirect(url_for('inventory.index'))
    
    # Delete inventory item
    if Inventory.delete_item(item_id):
        flash('Ingredient deleted successfully!', 'success')
    else:
        flash('Error deleting ingredient. Please try again.', 'danger')
    
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/suggestions')
@login_required
def suggestions():
    """API endpoint for ingredient name suggestions"""
    query = request.args.get('q', '')
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Get ingredient suggestions
    suggestions = Inventory.get_ingredient_suggestions(query)
    
    return jsonify(suggestions)

@inventory_bp.route('/ingredient-info')
@login_required
def ingredient_info():
    """API endpoint for ingredient metadata (unit, category)"""
    name = request.args.get('name', '')
    
    if not name:
        return jsonify({})
    
    # Get suggested unit for ingredient
    unit = Inventory.get_ingredient_unit(name)
    
    # Get suggested category for ingredient
    category = Inventory.get_ingredient_category(name)
    
    return jsonify({
        'unit': unit,
        'category': category
    })
