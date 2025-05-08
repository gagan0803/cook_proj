from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.recipe import Recipe
from models.inventory import Inventory
from forms import RecipeCompleteForm
import logging

logger = logging.getLogger(__name__)

recipe_bp = Blueprint('recipe', __name__)

@recipe_bp.route('/')
@login_required
def index():
    # Get all recipes
    recipes = Recipe.get_all()
    
    # Get user's dietary preferences
    preferences = current_user.get_preferences()
    
    # Filter recipes based on preferences
    if any(preferences.values()):
        dietary_filters = {
            key: value for key, value in preferences.items() if value
        }
        recipes = Recipe.filter_by_dietary(recipes, dietary_filters)
    
    return render_template('recipe/index.html', recipes=recipes)

@recipe_bp.route('/<recipe_id>')
@login_required
def detail(recipe_id):
    # Get recipe details
    recipe = Recipe.get_by_id(recipe_id)
    
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('recipe.index'))
    
    # Fix image URLs by using the updated get_image_path function
    if 'image_url' in recipe:
        recipe['image_url'] = Recipe.get_image_path(recipe_id, recipe['image_url'])
    
    # Check if user has all ingredients in inventory
    inventory_items = Inventory.get_by_user_id(current_user.id)
    
    # Create a dictionary of user's inventory for easy lookup
    user_inventory = {}
    for item in inventory_items:
        user_inventory[item.ingredient_name.lower()] = item
    
    # Check which ingredients are missing
    missing_ingredients = []
    for ingredient in recipe.get('ingredients', []):
        ingredient_name = ingredient.get('name', '').lower()
        
        # Check for exact match or partial match at beginning of name
        has_ingredient = any(
            inv_name.lower().startswith(ingredient_name) or ingredient_name.startswith(inv_name.lower()) 
            for inv_name in user_inventory.keys()
        )
        
        if not has_ingredient:
            missing_ingredients.append(ingredient)
    
    has_all_ingredients = len(missing_ingredients) == 0
    
    # Prepare form for marking recipe as completed
    form = RecipeCompleteForm()
    
    return render_template(
        'recipe/detail.html', 
        recipe=recipe, 
        has_all_ingredients=has_all_ingredients,
        missing_ingredients=missing_ingredients,
        form=form
    )

@recipe_bp.route('/search')
@login_required
def search():
    search_term = request.args.get('term', '')
    
    if not search_term:
        return render_template('recipe/search.html', recipes=[], search_term='')
    
    # Search for recipes by name and description
    recipes = Recipe.search_by_name(search_term)
    
    # Apply dietary filters if provided
    dietary_filters = {}
    for filter_name in ['vegetarian', 'vegan', 'gluten_free', 'dairy_free']:
        if request.args.get(filter_name) == 'on':
            dietary_filters[filter_name] = True
    
    if dietary_filters:
        recipes = Recipe.filter_by_dietary(recipes, dietary_filters)
    
    # Fix image URLs
    for recipe in recipes:
        if 'image_url' in recipe:
            recipe['image_url'] = Recipe.get_image_path(str(recipe['_id']), recipe['image_url'])
    
    return render_template('recipe/search.html', recipes=recipes, search_term=search_term)

@recipe_bp.route('/completed')
@login_required
def completed():
    # Get user's completed recipes
    completed_recipes = Recipe.get_completed_recipes(current_user.id)
    
    # Fix image URLs
    for item in completed_recipes:
        if item['recipe'] and 'image_url' in item['recipe']:
            item['recipe']['image_url'] = Recipe.get_image_path(
                str(item['recipe']['_id']), 
                item['recipe']['image_url']
            )
    
    return render_template('recipe/completed.html', completed_recipes=completed_recipes)

@recipe_bp.route('/<recipe_id>/complete', methods=['POST'])
@login_required
def complete(recipe_id):
    # Get recipe details
    recipe = Recipe.get_by_id(recipe_id)
    
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('recipe.index'))
    
    form = RecipeCompleteForm()
    
    if form.validate_on_submit():
        servings = form.servings.data
        
        # Mark recipe as completed
        if Recipe.mark_recipe_completed(current_user.id, recipe_id, servings):
            flash('Recipe marked as completed! Your inventory has been updated.', 'success')
        else:
            flash('Error marking recipe as completed.', 'danger')
    
    return redirect(url_for('recipe.completed'))

@recipe_bp.route('/suggestions')
@login_required
def suggestions():
    """API endpoint for recipe search suggestions"""
    query = request.args.get('q', '')
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Get ingredient suggestions
    suggestions = Recipe.get_ingredient_suggestions(query)
    
    return jsonify(suggestions)
