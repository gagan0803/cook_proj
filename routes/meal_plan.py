from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.meal_plan import MealPlan
from models.recipe import Recipe
from models.inventory import Inventory
from forms import MealPlanForm
from config import Config
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

meal_plan_bp = Blueprint('meal_plan', __name__)

@meal_plan_bp.route('/')
@login_required
def index():
    # Get current week's meal plan
    meal_plan = MealPlan.get_current_week(current_user.id)
    
    # Get days of week for the template
    days = dict(Config.DAYS_OF_WEEK)
    
    # Get meal types for the template
    meal_types = dict(Config.MEAL_TYPES)
    
    # Fix image URLs
    for item in meal_plan.items:
        if 'image_url' in item['recipe']:
            item['recipe']['image_url'] = Recipe.get_image_path(
                str(item['recipe']['_id']), 
                item['recipe']['image_url']
            )
    
    return render_template(
        'meal_plan/index.html', 
        meal_plan=meal_plan,
        days=days,
        meal_types=meal_types
    )

@meal_plan_bp.route('/add', methods=['POST'])
@login_required
def add():
    form = MealPlanForm()
    
    if form.validate_on_submit():
        # Get current week's meal plan
        meal_plan = MealPlan.get_current_week(current_user.id)
        
        # Add recipe to meal plan
        item_id = MealPlan.add_recipe(
            plan_id=meal_plan.id,
            recipe_id=form.recipe_id.data,
            day_of_week=form.day_of_week.data,
            meal_type=form.meal_type.data
        )
        
        if item_id:
            flash('Recipe added to meal plan!', 'success')
        else:
            flash('Error adding recipe to meal plan. Please try again.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'danger')
    
    # Determine redirect URL
    next_url = request.args.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('meal_plan.index'))

@meal_plan_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove(item_id):
    # Remove recipe from meal plan
    if MealPlan.remove_recipe(item_id):
        flash('Recipe removed from meal plan!', 'success')
    else:
        flash('Error removing recipe from meal plan. Please try again.', 'danger')
    
    return redirect(url_for('meal_plan.index'))

@meal_plan_bp.route('/grocery-list/<int:plan_id>')
@login_required
def grocery_list(plan_id):
    # Get meal plan
    meal_plan = MealPlan.get_by_id(plan_id)
    
    if not meal_plan or meal_plan.user_id != current_user.id:
        flash('Meal plan not found.', 'danger')
        return redirect(url_for('meal_plan.index'))
    
    # Get user's inventory
    inventory_items = Inventory.get_by_user_id(current_user.id)
    
    # Generate grocery list
    grocery_list = meal_plan.get_grocery_list(inventory_items)
    
    # Fix image URLs
    for item in meal_plan.items:
        if 'image_url' in item['recipe']:
            item['recipe']['image_url'] = Recipe.get_image_path(
                str(item['recipe']['_id']), 
                item['recipe']['image_url']
            )
    
    return render_template(
        'meal_plan/grocery_list.html', 
        meal_plan=meal_plan,
        grocery_list=grocery_list
    )
