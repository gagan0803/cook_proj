from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from database.mysql_setup import get_connection
import logging

logger = logging.getLogger(__name__)

class User(UserMixin):
    def __init__(self, id, username, email, password_hash=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get_by_id(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            return None
        
        return User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            password_hash=user['password']
        )
    
    @staticmethod
    def get_by_email(email):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            return None
        
        return User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            password_hash=user['password']
        )
    
    @staticmethod
    def get_by_username(username):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            return None
        
        return User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            password_hash=user['password']
        )
    
    @staticmethod
    def create(username, email, password):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create user instance
        user = User(id=None, username=username, email=email)
        user.set_password(password)
        
        try:
            # Insert user into database
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, user.password_hash)
            )
            
            user.id = cursor.lastrowid
            
            # Create default preferences for user
            cursor.execute(
                "INSERT INTO user_preferences (user_id) VALUES (%s)",
                (user.id,)
            )
            
            conn.commit()
            cursor.close()
            
            return user
        except Exception as e:
            conn.rollback()
            cursor.close()
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_preferences(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT * FROM user_preferences WHERE user_id = %s",
            (self.id,)
        )
        
        prefs = cursor.fetchone()
        cursor.close()
        
        # If no preferences exist, create default preferences
        if not prefs:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO user_preferences (user_id) VALUES (%s)",
                (self.id,)
            )
            
            conn.commit()
            cursor.close()
            
            return {
                'vegetarian': False,
                'vegan': False,
                'gluten_free': False,
                'dairy_free': False
            }
        
        return prefs
    
    def update_preferences(self, preferences):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                UPDATE user_preferences
                SET vegetarian = %s, vegan = %s, gluten_free = %s, dairy_free = %s
                WHERE user_id = %s
                """,
                (
                    preferences.get('vegetarian', False),
                    preferences.get('vegan', False),
                    preferences.get('gluten_free', False),
                    preferences.get('dairy_free', False),
                    self.id
                )
            )
            
            conn.commit()
            cursor.close()
            
            return True
        except Exception as e:
            conn.rollback()
            cursor.close()
            logger.error(f"Error updating user preferences: {e}")
            return False
