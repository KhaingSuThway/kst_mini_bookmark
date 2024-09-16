from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from spider import run_spider
import threading

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['recipe_database']
recipes_collection = db['recipes']

@app.route('/')
def index():
    recipes = list(recipes_collection.find({}, {'_id': 0}))
    return render_template('index.html', recipes=recipes)

@app.route('/scrape')
def scrape():
    thread = threading.Thread(target=run_spider)
    thread.start()
    return jsonify({"message": "Scraping started in the background!"})

if __name__ == '__main__':
    app.run(debug=True)