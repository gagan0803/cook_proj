from database.mysql_setup import get_connection
from datetime import datetime, timedelta
from models.recipe import Recipe
import logging

logger = logging.getLogger(__name__)

class MealPlan:
    def __init__(self, id, user_id, week_start_date, items=None):
        self.id = id
        self.user_id = user_id
        self.week_start_date = week_start_date
        self.items = items or []
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get all meal plans for a user"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(
                """
                SELECT * FROM meal_plans 
                WHERE user_id = %s 
                ORDER BY week_start_date DESC
                """,
                (user_id,)
            )
            
            meal_plans = []
            for plan in cursor.fetchall():
                # Get meal plan items
                cursor.execute(
                    """
                    SELECT * FROM meal_plan_items 
                    WHERE meal_plan_id = %s
                    """,
                    (plan['id'],)
                )
                
                items = []
                for item in cursor.fetchall():
                    # Get recipe details
                    recipe = Recipe.get_by_id(item['recipe_id'])
                    
                    if recipe:
                        items.append({
                            'id': item['id'],
                            'meal_plan_id': item['meal_plan_id'],
                            'recipe_id': item['recipe_id'],
                            'day_of_week': item['day_of_week'],
                            'meal_type': item['meal_type'],
                            'recipe': recipe
                        })
                
                meal_plans.append(MealPlan(
                    id=plan['id'],
                    user_id=plan['user_id'],
                    week_start_date=plan['week_start_date'],
                    items=items
                ))
            
            cursor.close()
            return meal_plans
        except Exception as e:
            cursor.close()
            logger.error(f"Error getting meal plans: {e}")
            return []
    
    @staticmethod
    def get_by_id(plan_id):
        """Get a meal plan by ID"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(
                """
                SELECT * FROM meal_plans 
                WHERE id = %s
                """,
                (plan_id,)
            )
            
            plan = cursor.fetchone()
            
            if not plan:
                cursor.close()
                return None
            
            # Get meal plan items
            cursor.execute(
                """
                SELECT * FROM meal_plan_items 
                WHERE meal_plan_id = %s
                """,
                (plan['id'],)
            )
            
            items = []
            for item in cursor.fetchall():
                # Get recipe details
                recipe = Recipe.get_by_id(item['recipe_id'])
                
                if recipe:
                    items.append({
                        'id': item['id'],
                        'meal_plan_id': item['meal_plan_id'],
                        'recipe_id': item['recipe_id'],
                        'day_of_week': item['day_of_week'],
                        'meal_type': item['meal_type'],
                        'recipe': recipe
                    })
            
            cursor.close()
            
            return MealPlan(
                id=plan['id'],
                user_id=plan['user_id'],
                week_start_date=plan['week_start_date'],
                items=items
            )
        except Exception as e:
            cursor.close()
            logger.error(f"Error getting meal plan: {e}")
            return None
    
    @staticmethod
    def get_current_week(user_id):
        """Get the current week's meal plan for a user"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Calculate the start of the current week (Monday)
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        
        try:
            cursor.execute(
                """
                SELECT * FROM meal_plans 
                WHERE user_id = %s AND week_start_date = %s
                """,
                (user_id, start_of_week)
            )
            
            plan = cursor.fetchone()
            
            # If no plan exists for the current week, create one
            if not plan:
                cursor.execute(
                    """
                    INSERT INTO meal_plans (user_id, week_start_date)
                    VALUES (%s, %s)
                    """,
                    (user_id, start_of_week)
                )
                
                conn.commit()
                
                plan_id = cursor.lastrowid
                
                cursor.close()
                
                return MealPlan(
                    id=plan_id,
                    user_id=user_id,
                    week_start_date=start_of_week,
                    items=[]
                )
            
            # Get meal plan items
            cursor.execute(
                """
                SELECT * FROM meal_plan_items 
                WHERE meal_plan_id = %s
                """,
                (plan['id'],)
            )
            
            items = []
            for item in cursor.fetchall():
                # Get recipe details
                recipe = Recipe.get_by_id(item['recipe_id'])
                
                if recipe:
                    items.append({
                        'id': item['id'],
                        'meal_plan_id': item['meal_plan_id'],
                        'recipe_id': item['recipe_id'],
                        'day_of_week': item['day_of_week'],
                        'meal_type': item['meal_type'],
                        'recipe': recipe
                    })
            
            cursor.close()
            
            return MealPlan(
                id=plan['id'],
                user_id=plan['user_id'],
                week_start_date=plan['week_start_date'],
                items=items
            )
        except Exception as e:
            conn.rollback()
            cursor.close()
            logger.error(f"Error getting current week meal plan: {e}")
            return None
    
    @staticmethod
    def add_recipe(plan_id, recipe_id, day_of_week, meal_type):
        """Add a recipe to a meal plan"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO meal_plan_items (meal_plan_id, recipe_id, day_of_week, meal_type)
                VALUES (%s, %s, %s, %s)
                """,
                (plan_id, recipe_id, day_of_week, meal_type)
            )
            
            conn.commit()
            item_id = cursor.lastrowid
            cursor.close()
            
            return item_id
        except Exception as e:
            conn.rollback()
            cursor.close()
            logger.error(f"Error adding recipe to meal plan: {e}")
            return None
    
    @staticmethod
    def remove_recipe(item_id):
        """Remove a recipe from a meal plan"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                DELETE FROM meal_plan_items 
                WHERE id = %s
                """,
                (item_id,)
            )
            
            conn.commit()
            cursor.close()
            
            return True
        except Exception as e:
            conn.rollback()
            cursor.close()
            logger.error(f"Error removing recipe from meal plan: {e}")
            return False
    
    def get_grocery_list(self, user_inventory=None):
        """
        Generate a grocery list for the meal plan
        
        Args:
            user_inventory (list, optional): List of inventory items
            
        Returns:
            list: List of ingredients needed for the meal plan
        """
        # Get all ingredients from recipes in the meal plan
        all_ingredients = {}
        
        for item in self.items:
            recipe = item.get('recipe')
            if not recipe:
                continue
            
            for ingredient in recipe.get('ingredients', []):
                name = ingredient.get('name', '').lower()
                amount = float(ingredient.get('amount', 0))
                unit = ingredient.get('unit', '')
                
                if name in all_ingredients:
                    # If the ingredient already exists, add the amount
                    if all_ingredients[name]['unit'] == unit:
                        all_ingredients[name]['amount'] += amount
                    else:
                        # If units don't match, keep them separate with a note
                        alt_key = f"{name} ({unit})"
                        if alt_key in all_ingredients:
                            all_ingredients[alt_key]['amount'] += amount
                        else:
                            all_ingredients[alt_key] = {
                                'name': name,
                                'amount': amount,
                                'unit': unit
                            }
                else:
                    all_ingredients[name] = {
                        'name': name,
                        'amount': amount,
                        'unit': unit
                    }
        
        # Subtract what the user already has in inventory
        if user_inventory:
            for item in user_inventory:
                name = item.ingredient_name.lower()
                if name in all_ingredients:
                    # If the units match, subtract the quantity
                    if all_ingredients[name]['unit'] == item.unit:
                        all_ingredients[name]['amount'] -= float(item.quantity)
                        
                        # If the amount is now zero or negative, remove the ingredient
                        if all_ingredients[name]['amount'] <= 0:
                            del all_ingredients[name]
                    # If units don't match, we can't subtract accurately
                    # So we leave it in the grocery list
        
        # Convert dictionary to list
        grocery_list = list(all_ingredients.values())
        
        # Round amounts to 2 decimal places for readability
        for item in grocery_list:
            item['amount'] = round(item['amount'], 2)
        
        # Sort by name
        grocery_list.sort(key=lambda x: x['name'])
        
        return grocery_list
