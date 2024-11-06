import os
from flask import Flask, render_template, request, url_for
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
import json
import os
import cv2
import configparser
import traceback
import os
import io
import base64
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import unicodedata

import boto3

from flask import Flask, render_template, request, url_for, send_from_directory
import json
from botocore.exceptions import ClientError
import pandas as pd
from sentence_transformers import SentenceTransformer
import certifi
from PIL import Image

from pathlib import Path
import base64
import io
from datetime import datetime
import hashlib
import threading
from functools import lru_cache

app = Flask(__name__)
#model = SentenceTransformer('all-MiniLM-L6-v2')
model = SentenceTransformer('all-MiniLM-L6-v2')


# Load the configuration
config = configparser.ConfigParser()
config_path = Path(__file__).parent / 'config' / 'config.ini'
config.read(str(config_path))


# Extract AWS credentials from the config file
aws_access_key = config.get('aws', 'aws_access_key_id')
aws_secret_key = config.get('aws', 'aws_secret_access_key')
aws_region = config.get('aws', 'region')
session = boto3.Session(
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)
# MongoDB setup
client = MongoClient(
    "mongodb+srv://admin:venkatesh123@cluster0.sttdr.mongodb.net/",
    tls=True,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=20000,
    retryWrites=True,
    w="majority"
)
db = client["prod"]
collection = db["recipes_embeddings"]
image_collection = db["generated_images"]  # New collection for image caching

# AWS Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2'
)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def create_bedrock_client():
    try:
        # Load config
        config_path = Path(__file__).parent / 'config' / 'config.ini'
        config.read(str(config_path))
        
        # Create AWS session
        session = boto3.Session(
            aws_access_key_id=config.get('aws', 'aws_access_key_id'),
            aws_secret_access_key=config.get('aws', 'aws_secret_access_key'),
            region_name='us-west-2'  # Explicitly set region
        )
        
        # Create bedrock runtime client
        bedrock_client = session.client(
            service_name='bedrock-runtime',
            endpoint_url='https://bedrock-runtime.us-west-2.amazonaws.com',  # Correct endpoint URL
            region_name='us-west-2'
        )
        
        return bedrock_client
    except Exception as e:
        print(f"Error creating Bedrock client: {e}")
        traceback.print_exc()
        return None
    
@app.route('/static/generated_images/<path:filename>')
def serve_image(filename):
    path = os.path.join(app.root_path, 'static', 'generated_images')
    if not os.path.exists(os.path.join(path, filename)):
        return "Image not found", 404
    response = send_from_directory(path, filename)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response
def get_image_hash(name):
    """Generate a unique hash for the image name"""
    return hashlib.md5(name.encode()).hexdigest()


def clean_json_string(json_str):
    """Clean and format JSON string properly"""
    # Replace single quotes with double quotes
    json_str = json_str.replace("'", '"')
    # Remove any newlines and extra spaces
    json_str = ' '.join(json_str.split())
    return json_str

def get_image_hash(name):
    """Generate a unique hash for the image name"""
    return hashlib.md5(name.encode()).hexdigest()

def check_image_cache(name):
    """Check if image exists in MongoDB cache"""
    image_hash = get_image_hash(name)
    cached_image = image_collection.find_one({"image_hash": image_hash})
    if cached_image:
        return cached_image["image_url"]
    return None

def save_to_image_cache(name, image_url):
    """Save generated image URL to MongoDB cache"""
    image_hash = get_image_hash(name)
    image_collection.update_one(
        {"image_hash": image_hash},
        {"$set": {"image_url": image_url, "created_at": datetime.now()}},
        upsert=True
    )

def generate_food_image_async(name, result):
    """Asynchronous image generation function without caching"""
    try:
        bedrock_client = create_bedrock_client()
        if not bedrock_client:
            raise Exception("Failed to create Bedrock client")
            
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": f"Professional food photography of {name}, on a clean plate, white background, high quality, 4k, detailed"
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 768,
                "width": 768,
                "cfgScale": 7.0,
                "seed": 0
            }
        }
        
        body = json.dumps(request_body)
        response = bedrock_client.invoke_model(
            modelId='amazon.titan-image-generator-v1',
            body=body.encode('utf-8'),
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        base64_image = response_body.get("images")[0]
        image_bytes = base64.b64decode(base64_image)
        
        image = Image.open(io.BytesIO(image_bytes))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{get_image_hash(name)}_{timestamp}.png"
        filepath = os.path.join('static/generated_images', filename)
        
        image = image.convert('RGB')
        image.save(filepath, optimize=True, quality=85)
        
        # Add timestamp to URL to prevent caching
        image_url = f"/static/generated_images/{filename}?t={timestamp}"
        result['image_url'] = image_url
        
        print("Image generation completed")
        
    except Exception as e:
        print(f"Image generation error: {e}")
        result['image_url'] = None

def get_food_info(prompt):
    try:

        
        client = create_bedrock_client()
        if not client:
            raise Exception("Failed to create Bedrock client")
        
        extraction_template = (
            "Given a food-related text that asks for dishes similar to a reference dish, extract the following in JSON format:\n"
            "1. DISH NAME: Always use the reference dish mentioned in the prompt (the dish that similarities are being requested for) "
            "as the DISH NAME. For example, if the prompt asks for 'dishes similar to X', then X should be the DISH NAME.\n"
            "2. INGREDIENTS: List all ingredients for the DISH NAME (not the similar dishes) as quantity,description. "
            "Include both explicit ingredients (directly stated) and implicit ingredients (essential components based on the dish description).\n"
            "3. Cuisine: Identify the cuisine of the DISH NAME (not the cuisine of similar dishes).\n"
            "4. Course: Specify if the DISH NAME is a Snack or Main course.\n"
            "5. Diet: Indicate if the DISH NAME is Vegetarian or Non Vegetarian.\n"
            "6. Generated_Description: First describe the DISH NAME briefly, then mention similar dishes from the requested cuisine, "
            "explaining how they are similar in terms of ingredients, preparation, or serving style.\n"
        )
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": "System:" + extraction_template + "\n\nHuman: " + prompt + "\n\nAssistant:"
                }
            ]
        }
        
        response = client.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps(request_body)
        )
        
        if response and 'body' in response:
            response_body = json.loads(response['body'].read().decode('utf-8'))
            print("Raw response:", response_body)  # Debug print
            
            # Handle the nested structure
            if 'content' in response_body and isinstance(response_body['content'], list):
                for content_item in response_body['content']:
                    if content_item.get('type') == 'text':
                        text_content = content_item.get('text', '')
                        # Find the JSON part in the text
                        try:
                            # Find the JSON object in the text
                            json_start = text_content.find('{')
                            json_end = text_content.rfind('}') + 1
                            if json_start >= 0 and json_end > json_start:
                                json_str = text_content[json_start:json_end]
                                food_data = json.loads(json_str)
                                return [{"text": json.dumps(food_data)}]
                        except json.JSONDecodeError as e:
                            print(f"JSON parse error: {e}")
                            print("Text content:", text_content)
                            continue
            
            print("No valid JSON found in response")
            return None
                
        return None
            
    except Exception as e:
        print(f"Error in get_food_info: {e}")
        traceback.print_exc()
        return None


def process_food_data(extracted_info, model):
    print("In process_food_data")
    try:
        # Handle the extracted info structure
        if isinstance(extracted_info, list) and len(extracted_info) > 0:
            if isinstance(extracted_info[0], dict) and 'text' in extracted_info[0]:
                try:
                    food_data = json.loads(extracted_info[0]['text'])
                    print("food data json generated")
                except json.JSONDecodeError:
                    print("Error parsing JSON from text")
                    return None, None
            else:
                food_data = extracted_info[0]
        else:
            print("Invalid extracted_info format")
            return None, None

        # Process ingredients
        ingredients = food_data.get('INGREDIENTS', [])
        if isinstance(ingredients, list):
            ingredients_text = ', '.join(str(i) for i in ingredients)
        else:
            ingredients_text = str(ingredients)

        # Process diet - Create a fixed 4-dimensional encoding
        diet = food_data.get('Diet', '').lower()
        
        # Create a fixed 4-dimensional diet encoding
        diet_embedding = [0, 0, 0, 0]  # Initialize with zeros
        
        if 'non' in diet and 'vegetarian' in diet:
            diet_embedding = [1.0, 0.0, 0.0]  # Non-vegetarian
        elif 'vegetarian' in diet:
            diet_embedding = [0.0, 1.0, 0.0]  # Vegetarian
        
        # print("Diet embedding created")
        # print(diet_embedding)

        # Create ingredients embedding
        ingredients_embedding = model.encode(ingredients_text, show_progress_bar=False)
        
        return ingredients_embedding.tolist()
        
    except Exception as e:
        print(f"Error in process_food_data: {e}")
        traceback.print_exc()
        return None, None
   
# Within your find_similar_foods function
def find_similar_foods(query_embedding, diet_type, num_results=2):
    print("query_embedding")
    print(query_embedding)
    try:
        if query_embedding is None:
            print("Missing embeddings")
            return []
            
        if not isinstance(query_embedding, list):
            print(f"Invalid embedding format")
            return []
        
        # Vector search with diet filter
        results = list(collection.aggregate([
            {
                "$vectorSearch": {
                    "index": "diet_vector_index",
                    "path": "ingredients_embeddings",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": 10,
                    "similarityMetric": "cosine"
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
        ]))

        print(f"Found {len(results)} matching results for {diet_type} diet")

        # Generate images for results
        threads = []
        for result in results:
            result.setdefault('Cuisine', 'Unknown')
            result.setdefault('Diet', diet_type)
            result.setdefault('PrepTime', 'Unknown')
            result.setdefault('CookTimeIn', 'Unknown')
            result.setdefault('Generated_Description', 'No description available.')
            
            thread = threading.Thread(
                target=generate_food_image_async,
                args=(result.get('name', ''), result)
            )
            thread.start()
            threads.append(thread)
        
        # Ensure all threads complete before returning results
        for thread in threads:
            thread.join(timeout=20)  # Increased timeout to 30 seconds

        # Check for image URLs in results
        for result in results:
            if 'image_url' not in result or result['image_url'] is None:
                print(f"Image generation failed for {result.get('name', '')}")

        return results
        
    except Exception as e:
        print(f"Error in find_similar_foods: {e}")
        traceback.print_exc()
        return [] 


@app.route("/image_search", methods=["POST"])
def image_search():
    try:
        if 'food_image' not in request.files:
            return render_template(
                "error.html",
                error="No image file uploaded"
            )
            
        file = request.files['food_image']
        if file.filename == '':
            return render_template(
                "error.html",
                error="No image selected"
            )
            
        if file:
            # Read and process the image
            image_bytes = file.read()
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to RGB for model processing
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Process image with your model
            # This is where you'd add your image processing logic
            # For now, we'll just return an error
            return render_template(
                "error.html",
                error="Image search functionality is coming soon!"
            )
            
    except Exception as e:
        print(f"Error in image search: {e}")
        traceback.print_exc()
        return render_template(
            "error.html",
            error="An error occurred while processing your image"
        )


@app.route("/", methods=["GET", "POST"])
def index():
    try:
        if request.method == "POST":
            query = request.form["query"]
            
            # Get food info
            extracted_info = get_food_info(query)
            
            if not extracted_info:
                return render_template(
                    "error.html", 
                    error="Could not understand the food query. Please try being more specific."
                )
            
            try:
                info_dict = json.loads(extracted_info[0]['text'])
                diet_type = info_dict.get('Diet', 'Vegetarian')
                
                # Process ingredients
                ingredients_embedding = process_food_data(extracted_info, model)
                if not ingredients_embedding:
                    return render_template(
                        "error.html",
                        error="Could not analyze the food data. Please try a different query."
                    )
                
                # Find similar foods
                results = find_similar_foods(ingredients_embedding, diet_type)
                if not results:
                    return render_template(
                        "error.html",
                        error=f"No similar {diet_type.lower()} dishes found. Please try a different query."
                    )
                
                return render_template(
                    "results.html",
                    query=query,
                    results=results,
                    original_diet=diet_type
                )
                
            except Exception as e:
                print(f"Error processing query: {e}")
                traceback.print_exc()
                return render_template(
                    "error.html",
                    error="An error occurred while processing your request. Please try again."
                )
                
        return render_template("index.html")
        
    except Exception as e:
        print(f"Error in index route: {e}")
        traceback.print_exc()
        return render_template(
            "error.html",
            error="An unexpected error occurred. Please try again."
        )
if __name__ == "__main__":
    # Ensure the generated images directory exists
    os.makedirs('static/generated_images', exist_ok=True)
    app.run(debug=True, port=int(os.getenv('PORT', 4439)))