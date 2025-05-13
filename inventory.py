from database.mysql_setup import get_connection
from database.mongo_setup import mongo_db
from datetime import datetime, timedelta

class Inventory:
    @staticmethod
    def update_quantity(user_id, ingredient_name, quantity_change):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, quantity FROM inventory WHERE user_id = %s AND ingredient_name = %s",
                (user_id, ingredient_name)
            )
            item = cursor.fetchone()
            
            if item:
                item_id, current_quantity = item
                new_quantity = round(current_quantity + quantity_change, 2)
                
                # Delete if quantity is zero or less
                if new_quantity <= 0:
                    cursor.execute("DELETE FROM inventory WHERE id = %s", (item_id,))
                else:
                    cursor.execute(
                        "UPDATE inventory SET quantity = %s WHERE id = %s",
                        (new_quantity, item_id)
                    )
                
                conn.commit()
                cursor.close()
                return True
            else:
                cursor.close()
                return False
        except Exception as e:
            conn.rollback()
            cursor.close()
            print(f"Error updating quantity: {e}")
            return False
