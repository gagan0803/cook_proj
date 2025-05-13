from database.mongo_setup import mongo_db

class Recipe:
    @staticmethod
    def search_suggestions(search_term):
        if not search_term:
            return []
        # Fetch up to 10 recipe name suggestions
        return list(mongo_db.recipes.find({"name": {"$regex": f"^{search_term}", "$options": "i"}}).limit(10))
