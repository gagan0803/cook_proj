from database.mysql_setup import get_connection
from datetime import datetime, timedelta
from config import Config
from database.mongo_setup import mongo_db
import pymongo
import re
import logging

logger = logging.getLogger(__name__)

class Inventory:
    def __init__(self, id, user_id, ingredient_name, category, quantity, unit, expiry_date=None, added_date=None, ingredient_id=None):
        self.id = id
        self.user_id = user_id
        self.ingredient_name = ingredient_name
        self.category = category
        self.quantity = quantity
        self.unit = unit
        self.expiry_date = expiry_date
        self.added_date = added_date
        self.ingredient_id = ingredient_id
    
    @staticmethod
    def get_by_user_id(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(
                "SELECT * FROM inventory WHERE user_id = %s ORDER BY ingredient_name",
                (user_id,)
            )
            
            inventory_items = []
            for item in cursor.fetchall():
                inventory_items.append(Inventory(
                    id=item['id'],
                    user_id=item['user_id'],
                    ingredient_name=item['ingredient_name'],
                    category=item['category'],
                    quantity=item['quantity'],
                    unit=item['unit'],
                    expiry_date=item['expiry_date'],
                    added_date=item['added_date'],
                    ingredient_id=item.get('ingredient_id')
                ))
            
            cursor.close()
            return inventory_items
        except Exception as e:
            cursor.close()
            logger.error(f"Error getting inventory items: {e}")
            return []
    
    @staticmethod
    def get_by_id(item_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM inventory WHERE id = %s", (item_id,))
            item = cursor.fetchone()
            cursor.close()
            
            if not item:
                return None
            
            return Inventory(
                id=item['id'],
                user_id=item['user_id'],
                ingredient_name=item['ingredient_name'],
                category=item['category'],
                quantity=item['quantity'],
                unit=item['unit'],
                expiry_date=item['expiry_date'],
                added_date=item['added_date'],
                ingredient_id=item.get('ingredient_id')
            )
        except Exception as e:
            cursor.close()
            logger.error(f"Error getting inventory item: {e}")
            return None
    
    @staticmethod
    def get_ingredient_id(ingredient_name):
        """Get MongoDB ObjectID for an ingredient by name"""
        try:
            # Normalize ingredient name to lowercase
            ingredient_name = ingredient_name.lower()
            
            # Search for the ingredient in the recipes collection using case-insensitive regex
            results = mongo_db.recipes.aggregate([
                {"$unwind": "$ingredients"},
                {"$match": {"ingredients.name": {"$regex": f"^{re.escape(ingredient_name)}", "$options": "i"}}},
                {"$limit": 1}
            ])
            
            results_list = list(results)
            if results_list:
                # Return the MongoDB ObjectID as a string
                return str(results_list[0]['_id'])
            
            return None
        except Exception as e:
            logger.error(f"Error getting ingredient ID: {e}")
            return None
    
    @staticmethod
    def get_ingredient_unit(ingredient_name):
        """Get standard unit for an ingredient by name"""
        try:
            # Normalize ingredient name to lowercase
            ingredient_name = ingredient_name.lower()
            
            # Search for the ingredient using case-insensitive regex
            results = mongo_db.recipes.aggregate([
                {"$unwind": "$ingredients"},
                {"$match": {"ingredients.name": {"$regex": f"^{re.escape(ingredient_name)}", "$options": "i"}}},
                {"$limit": 1}
            ])
            
            results_list = list(results)
            if results_list:
                # Return the unit
                return results_list[0]['ingredients']['unit']
            
            return None
        except Exception as e:
            logger.error(f"Error getting ingredient unit: {e}")
            return None
    
    @staticmethod
    def get_ingredient_category(ingredient_name):
        """Get suggested category for an ingredient based on recipes"""
        try:
            # Normalize ingredient name to lowercase
            ingredient_name = ingredient_name.lower()
            
            # Try to find the ingredient in existing inventory items
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(
                "SELECT category FROM inventory WHERE LOWER(ingredient_name) LIKE %s LIMIT 1",
                (f"{ingredient_name}%",)
            )
            
            existing = cursor.fetchone()
            cursor.close()
            
            if existing:
                return existing['category']
            
            # Fallback category mapping based on common ingredients
            category_keywords = {
                'produce': ['vegetable', 'fruit', 'tomato', 'carrot', 'lettuce', 'apple', 'banana', 'orange', 'onion', 'garlic'],
                'meat': ['beef', 'chicken', 'pork', 'lamb', 'turkey', 'meat', 'fish', 'seafood', 'steak', 'bacon'],
                'dairy': ['milk', 'cheese', 'yogurt', 'cream', 'butter', 'egg'],
                'bakery': ['bread', 'bun', 'cake', 'pastry', 'dough', 'roll'],
                'pantry': ['rice', 'pasta', 'bean', 'lentil', 'flour', 'sugar', 'oil', 'vinegar', 'sauce'],
                'frozen': ['frozen', 'ice'],
                'spices': ['spice', 'herb', 'salt', 'pepper', 'cinnamon', 'oregano', 'basil', 'thyme'],
                'beverages': ['water', 'juice', 'soda', 'wine', 'beer', 'coffee', 'tea'],
            }
            
            # Check if the ingredient name contains any keywords
            for category, keywords in category_keywords.items():
                if any(keyword in ingredient_name for keyword in keywords):
                    return category
            
            return 'other'  # Default category
        except Exception as e:
            logger.error(f"Error getting ingredient category: {e}")
            return 'other'  # Default category on error
    
    @staticmethod
    def add_item(user_id, ingredient_name, category, quantity, unit, expiry_date=None):
        # First check if the ingredient exists in MongoDB
        ingredient_id = Inventory.get_ingredient_id(ingredient_name)
        
        if not ingredient_id:
            logger.warning(f"Ingredient not found in MongoDB: {ingredient_name}")
            # We'll still add it to the inventory even if not in recipe database
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if table has ingredient_id column
            cursor.execute("SHOW COLUMNS FROM inventory LIKE 'ingredient_id'")
            has_ingredient_id = cursor.fetchone() is not None
            
            if has_ingredient_id and ingredient_id:
                cursor.execute(
                    """
                    INSERT INTO inventory 
                    (user_id, ingredient_name, category, quantity, unit, expiry_date, ingredient_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, ingredient_name, category, quantity, unit, expiry_date, ingredient_id)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO inventory 
                    (user_id, ingredient_name, category, quantity, unit, expiry_date) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, ingredient_name, category, quantity, unit, expiry_date)
                )
                
            conn.commit()
            item_id = cursor.lastrowid
            cursor.close()
            
            return Inventory.get_by_id(item_id)
        except Exception as e:
            conn.rollback()
            cursor.close()
            logger.error(f"Error adding inventory item: {e}")
            return None
    
    @staticmethod
    def update_item(item_id, ingredient_name, category, quantity, unit, expiry_date=None):
        # First check if the ingredient exists in MongoDB
        ingredient_id = Inventory.get_ingredient_id(ingredient_name)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if table has ingredient_id column
            cursor.execute("SHOW COLUMNS FROM inventory LIKE 'ingredient_id'")
            has_ingredient_id = cursor.fetchone() is not None
            
            if has_ingredient_id and ingredient_id:
                cursor.execute(
                    """
                    UPDATE inventory 
                    SET ingredient_name = %s, category = %s, quantity = %s, unit = %s, expiry_date = %s, ingredient_id = %s
                    WHERE id = %s
                    """,
                    (ingredient_name, category, quantity, unit, expiry_date, ingredient_id, item_id)
                )
            else:
                cursor.execute(
                    """
                    UPDATE inventory 
                    SET ingredient_name = %s, category = %s, quantity = %s, unit = %s, expiry_date = %s
                    WHERE id = %s
                    """,
                    (ingredient_name, category, quantity, unit, expiry_date, item_id)
                )
                
            conn.commit()
            cursor.close()
            
            return Inventory.get_by_id(item_id)
        except Exception as e:
            conn.rollback()
            cursor.close()
            logger.error(f"Error updating inventory item: {e}")
            return None
    
    @staticmethod
    def delete_item(item_id):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM inventory WHERE id = %s", (item_id,))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            cursor.close()
            logger.error(f"Error deleting inventory item: {e}")
            return False
    
    @staticmethod
    def get_expiring_items(user_id, days=3):
        """Get inventory items that are expiring soon or already expired"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        today = datetime.now().date()
        expiry_date = today + timedelta(days=days)
        
        try:
            cursor.execute(
                """
                SELECT * FROM inventory 
                WHERE user_id = %s AND expiry_date IS NOT NULL 
                AND expiry_date <= %s
                ORDER BY expiry_date
                """,
                (user_id, expiry_date)
            )
            
            items = []
            for item in cursor.fetchall():
                items.append(Inventory(
                    id=item['id'],
                    user_id=item['user_id'],
                    ingredient_name=item['ingredient_name'],
                    category=item['category'],
                    quantity=item['quantity'],
                    unit=item['unit'],
                    expiry_date=item['expiry_date'],
                    added_date=item['added_date'],
                    ingredient_id=item.get('ingredient_id')
                ))
            
            cursor.close()
            return items
        except Exception as e:
            cursor.close()
            logger.error(f"Error getting expiring items: {e}")
            return []
    
    @staticmethod
    def get_ingredient_suggestions(query):
        """Get ingredient name suggestions for autocomplete"""
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
