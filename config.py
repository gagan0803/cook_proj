import os

class Config:
    # Database settings
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/cookbookit')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'cookbookit')
    
    # Application settings
    RECIPES_PER_PAGE = 12
    INVENTORY_EXPIRY_WARNING_DAYS = 3
    
    # Categories for ingredients
    INGREDIENT_CATEGORIES = [
        ('produce', 'Produce'),
        ('meat', 'Meat & Seafood'),
        ('dairy', 'Dairy & Eggs'),
        ('bakery', 'Bakery'),
        ('pantry', 'Pantry Items'),
        ('frozen', 'Frozen Foods'),
        ('spices', 'Spices & Herbs'),
        ('beverages', 'Beverages'),
        ('other', 'Other')
    ]
    
    # Units for ingredients
    INGREDIENT_UNITS = [
        ('g', 'Grams (g)'),
        ('kg', 'Kilograms (kg)'),
        ('mg', 'Milligrams (mg)'),
        ('oz', 'Ounces (oz)'),
        ('lb', 'Pounds (lb)'),
        ('ml', 'Milliliters (ml)'),
        ('l', 'Liters (l)'),
        ('tsp', 'Teaspoon (tsp)'),
        ('tbsp', 'Tablespoon (tbsp)'),
        ('cup', 'Cup'),
        ('pint', 'Pint'),
        ('quart', 'Quart'),
        ('gallon', 'Gallon'),
        ('piece', 'Piece'),
        ('slice', 'Slice'),
        ('whole', 'Whole'),
        ('pinch', 'Pinch'),
        ('bunch', 'Bunch'),
        ('clove', 'Clove'),
        ('count', 'Count')
    ]
    
    # Meal types for meal planning
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('dessert', 'Dessert')
    ]
    
    # Days of the week for meal planning
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ]
