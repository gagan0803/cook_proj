import os
import mysql.connector
import logging
from config import Config

logger = logging.getLogger(__name__)

# Connection pool
mysql_pool = None

def setup_mysql():
    """Setup MySQL connection pool"""
    global mysql_pool
    
    try:
        # Create connection pool
        mysql_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="cookbookit_pool",
            pool_size=5,
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        
        logger.info(f"Connected to MySQL: {Config.MYSQL_DB}")
        
        # Initialize database tables if they don't exist
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(64) NOT NULL UNIQUE,
                email VARCHAR(120) NOT NULL UNIQUE,
                password VARCHAR(256) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create inventory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                ingredient_name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                quantity FLOAT NOT NULL,
                unit VARCHAR(20) NOT NULL,
                expiry_date DATE,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ingredient_id VARCHAR(50),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create meal_plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meal_plans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                week_start_date DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create meal_plan_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meal_plan_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                meal_plan_id INT NOT NULL,
                recipe_id VARCHAR(50) NOT NULL,
                day_of_week INT NOT NULL,
                meal_type VARCHAR(20) NOT NULL,
                FOREIGN KEY (meal_plan_id) REFERENCES meal_plans(id) ON DELETE CASCADE
            )
        """)
        
        # Create completed_recipes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS completed_recipes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                recipe_id VARCHAR(50) NOT NULL,
                completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                servings_made INT NOT NULL DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create user_preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INT PRIMARY KEY,
                vegetarian BOOLEAN DEFAULT FALSE,
                vegan BOOLEAN DEFAULT FALSE,
                gluten_free BOOLEAN DEFAULT FALSE,
                dairy_free BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        cursor.close()
        conn.close()
        
        logger.info("MySQL tables initialized")
    except Exception as e:
        logger.error(f"MySQL setup error: {e}")
        raise

def get_connection():
    """Get a connection from the pool"""
    global mysql_pool
    
    if mysql_pool is None:
        setup_mysql()
        
    return mysql_pool.get_connection()
