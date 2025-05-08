from database.mongo_setup import mongo_db
from bson.objectid import ObjectId
import os
import re
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class Recipe:
    @staticmethod
    def get_image_path(recipe_id, image_url=None):
        """Return the local path to a recipe image or use placeholder if it doesn't exist"""
        try:
            # First try using recipe ID-based filename
            local_path = f"images/recipes/{recipe_id}.jpg"
            full_path = os.path.join(current_app.static_folder, local_path)
            
            if os.path.exists(full_path):
                return f"/static/{local_path}"
            
            # If image_url is provided, use it as fallback
            if image_url:
                return image_url
            
            # Fall back to placeholder
            return "/static/images/placeholder.jpg"
        except Exception as e:
            logger.error(f"Error getting image path: {e}")
            return "/static/images/placeholder.jpg"
        
    @staticmethod
    def get_all():
        try:
            return list(mongo_db.recipes.find())
        except Exception as e:
            logger.error(f"Error getting all recipes: {e}")
            return []
    
    @staticmethod
    def get_by_id(recipe_id):
        try:
            return mongo_db.recipes.find_one({"_id": ObjectId(recipe_id)})
        except Exception as e:
            logger.error(f"Error getting recipe by ID: {e}")
            return None
    
    @staticmethod
    def search_by_ingredients(ingredients_list, exclude_ingredients=None):
        """
        Search for recipes that can be made with the given ingredients
        
        Args:
            ingredients_list (list): List of ingredients names
            exclude_ingredients (list, optional): List of ingredients to exclude
            
        Returns:
            list: List of recipes that can be made with the given ingredients
        """
        if not ingredients_list:
            return []
        
        try:
            # Normalize ingredient names to lowercase for case-insensitive matching
            ingredients_list = [name.lower() for name in ingredients_list]
            
            # Create regex patterns for partial matching
            ingredient_patterns = [
                {"ingredients.name": {"$regex": f"^{re.escape(ingredient)}", "$options": "i"}}
                for ingredient in ingredients_list
            ]
            
            # Create query to match recipes with ingredients from the list
            query = {"$or": ingredient_patterns}
            
            # Add exclusion if provided
            if exclude_ingredients:
                exclude_ingredients = [name.lower() for name in exclude_ingredients]
                exclude_patterns = [
                    {"ingredients.name": {"$regex": f"^{re.escape(ingredient)}", "$options": "i"}}
                    for ingredient in exclude_ingredients
                ]
                query["$nor"] = exclude_patterns
            
            # Find recipes and calculate match percentage
            recipes = list(mongo_db.recipes.find(query))
            
            # Calculate match percentage for each recipe
            for recipe in recipes:
                total_ingredients = len(recipe["ingredients"])
                matching_ingredients = 0
                
                # Count matching ingredients with case-insensitive comparison
                for recipe_ingredient in recipe["ingredients"]:
                    ingredient_name = recipe_ingredient["name"].lower()
                    if any(ingredient_name.startswith(user_ingredient) for user_ingredient in ingredients_list):
                        matching_ingredients += 1
                
                recipe["match_percentage"] = (matching_ingredients / total_ingredients) * 100
            
            # Sort by match percentage (highest first)
            recipes.sort(key=lambda x: x.get("match_percentage", 0), reverse=True)
            
            return recipes
        except Exception as e:
            logger.error(f"Error searching recipes by ingredients: {e}")
            return []
    
    @staticmethod
    def filter_by_dietary(recipes, dietary_filters):
        """
        Filter recipes based on dietary preferences
        
        Args:
            recipes (list): List of recipes to filter
            dietary_filters (dict): Dictionary of dietary filters
            
        Returns:
            list: Filtered list of recipes
        """
        if not dietary_filters:
            return recipes
        
        try:
            filtered_recipes = []
            
            for recipe in recipes:
                # Check if recipe matches all dietary filters
                matches_all = True
                
                for key, value in dietary_filters.items():
                    if value and recipe.get("dietary_info", {}).get(key) != value:
                        matches_all = False
                        break
                
                if matches_all:
                    filtered_recipes.append(recipe)
            
            return filtered_recipes
        except Exception as e:
            logger.error(f"Error filtering recipes by dietary preferences: {e}")
            return recipes
    
    @staticmethod
    def filter_by_time(recipes, max_time):
        """
        Filter recipes by maximum time
        
        Args:
            recipes (list): List of recipes to filter
            max_time (int): Maximum total time in minutes
            
        Returns:
            list: Filtered list of recipes
        """
        if not max_time:
            return recipes
        
        try:
            return [r for r in recipes if (r.get('prep_time', 0) + r.get('cook_time', 0)) <= max_time]
        except Exception as e:
            logger.error(f"Error filtering recipes by time: {e}")
            return recipes
    
    @staticmethod
    def filter_by_difficulty(recipes, difficulty):
        """
        Filter recipes by difficulty level
        
        Args:
            recipes (list): List of recipes to filter
            difficulty (str): Difficulty level ('Easy', 'Medium', 'Hard')
            
        Returns:
            list: Filtered list of recipes
        """
        if not difficulty:
            return recipes
        
        try:
            return [r for r in recipes if r.get('difficulty') == difficulty]
        except Exception as e:
            logger.error(f"Error filtering recipes by difficulty: {e}")
            return recipes
    
    @staticmethod
    def search_by_name(search_term):
        """
        Search for recipes by name
        
        Args:
            search_term (str): Term to search for
            
        Returns:
            list: List of recipes matching the search term
        """
        if not search_term:
            return []
        
        try:
            # Create text index if it doesn't exist
            if "name_text" not in mongo_db.recipes.index_information():
                mongo_db.recipes.create_index([
                    ("name", "text"), 
                    ("description", "text"),
                    ("ingredients.name", "text")
                ])
            
            # Use text search with case insensitivity
            return list(mongo_db.recipes.find(
                {"$text": {"$search": search_term}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]))
        except Exception as e:
            logger.error(f"Error searching recipes by name: {e}")
            return []
    
    @staticmethod
    def get_recipe_ingredients(recipe_id):
        """
        Get ingredients for a specific recipe
        
        Args:
            recipe_id (str): Recipe ID
            
        Returns:
            list: List of ingredients for the recipe
        """
        recipe = Recipe.get_by_id(recipe_id)
        if not recipe:
            return []
        
        return recipe.get("ingredients", [])
    
    @staticmethod
    def get_ingredient_suggestions(query):
        """
        Get ingredient suggestions for autocomplete
        
        Args:
            query (str): Search query
            
        Returns:
            list: List of ingredient suggestions
        """
        if not query or len(query) < 2:
            return []
        
        try:
            # Normalize query to lowercase
            query = query.lower()
            
            # Aggregate unique ingredient names that match the query
            pipeline = [
                {"$unwind": "$ingredients"},
                {"$match": {"ingredients.name": {"$regex": f"^{re.escape(query)}", "$options": "i"}}},
                {"$group": {"_id": "$ingredients.name"}},
                {"$sort": {"_id": 1}},
                {"$limit": 10}
            ]
            
            results = mongo_db.recipes.aggregate(pipeline)
            
            # Return a list of ingredient names
            return [result["_id"] for result in results]
        except Exception as e:
            logger.error(f"Error getting ingredient suggestions: {e}")
            return []
    
    @staticmethod
    def mark_recipe_completed(user_id, recipe_id, servings=1):
        """
        Mark a recipe as completed by a user
        
        Args:
            user_id (int): User ID
            recipe_id (str): Recipe ID
            servings (int): Number of servings made
            
        Returns:
            bool: True if successful, False otherwise
        """
        from database.mysql_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO completed_recipes 
                (user_id, recipe_id, servings_made) 
                VALUES (%s, %s, %s)
                """,
                (user_id, recipe_id, servings)
            )
            
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            cursor.close()
            logger.error(f"Error marking recipe as completed: {e}")
            return False
    
    @staticmethod
    def get_completed_recipes(user_id):
        """
        Get recipes completed by a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of completed recipes with recipe details
        """
        from database.mysql_setup import get_connection
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(
                """
                SELECT * FROM completed_recipes 
                WHERE user_id = %s 
                ORDER BY completed_date DESC
                """,
                (user_id,)
            )
            
            completed = cursor.fetchall()
            cursor.close()
            
            # Fetch recipe details for each completed recipe
            for item in completed:
                item['recipe'] = Recipe.get_by_id(item['recipe_id'])
            
            return completed
        except Exception as e:
            cursor.close()
            logger.error(f"Error getting completed recipes: {e}")
            return []
