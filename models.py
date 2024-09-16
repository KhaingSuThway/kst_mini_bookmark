from pymongo import MongoClient
from bson import ObjectId

class MongoDB:
    def __init__(self, host='localhost', port=27017, db_name='recipe_database'):
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.recipes = self.db.recipes

    def get_all_recipes(self):
        return list(self.recipes.find())

    def get_recipe(self, recipe_id):
        return self.recipes.find_one({'_id': ObjectId(recipe_id)})

    # Add other methods as needed

# Create an instance of the MongoDB class
db = MongoDB()

# Example recipe structure
recipe_structure = {
    'name': str,
    'ingredients': str,
    'instructions': str,
    
}
