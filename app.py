import os
import logging
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "development_secret_key")

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import database setups
from database.mongo_setup import setup_mongo
from database.mysql_setup import setup_mysql

# Initialize databases
setup_mongo()
setup_mysql()

# Import User model for login manager
from models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Make datetime available in templates
@app.context_processor
def inject_now():
    return {'datetime': datetime}

# Import routes
from routes.auth import auth_bp
from routes.recipe import recipe_bp
from routes.inventory import inventory_bp
from routes.meal_plan import meal_plan_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(recipe_bp, url_prefix='/recipe')
app.register_blueprint(inventory_bp, url_prefix='/inventory')
app.register_blueprint(meal_plan_bp, url_prefix='/meal-plan')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Internal server error: {e}")
    return render_template('500.html'), 500

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Diagnostic routes
@app.route('/diagnose/mongo')
def diagnose_mongo():
    from database.mongo_setup import mongo_db
    try:
        collections = mongo_db.list_collection_names()
        recipe_count = mongo_db.recipes.count_documents({})
        return {
            "status": "connected",
            "collections": collections,
            "recipe_count": recipe_count
        }
    except Exception as e:
        logger.error(f"MongoDB diagnostic error: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/diagnose/mysql')
def diagnose_mysql():
    from database.mysql_setup import get_connection
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        return {
            "status": "connected",
            "tables": tables
        }
    except Exception as e:
        logger.error(f"MySQL diagnostic error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
