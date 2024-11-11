from pymongo import MongoClient
from config.settings import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_RECIPES, MONGO_COLLECTION_IMAGES
from datetime import datetime

class MongoService:
    def __init__(self):
        self.client = MongoClient(
            MONGO_URI,
            tls=True,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=20000,
            retryWrites=True,
            w="majority"
        )
        self.db = self.client[MONGO_DB_NAME]
        self.recipes_collection = self.db[MONGO_COLLECTION_RECIPES]
        self.images_collection = self.db[MONGO_COLLECTION_IMAGES]

    def find_similar_foods(self, query_embedding, diet_type, num_results=2):
        try:
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "diet_vector_index",
                        "path": "ingredients_embedding",
                        "queryVector": query_embedding,
                        "numCandidates": 100,
                        "limit": 3
                    }
                },
                {
                    "$match": {
                        "Diet": diet_type
                    }
                },
                {
                    "$project": {
                        "name": 1,
                        "Cuisine": 1,
                        "Diet": 1,
                        "PrepTime": 1,
                        "CookTimeIn": 1,
                        "Generated_Description": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                },
                {
                    "$limit": num_results
                }
            ]
            
            return list(self.recipes_collection.aggregate(pipeline))
        except Exception as e:
            print(f"Error in find_similar_foods: {e}")
            return []

    def check_image_cache(self, image_hash):
        return self.images_collection.find_one({"image_hash": image_hash})

    def save_to_image_cache(self, image_hash, image_url):
        self.images_collection.update_one(
            {"image_hash": image_hash},
            {"$set": {"image_url": image_url, "created_at": datetime.now()}},
            upsert=True
        )