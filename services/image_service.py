import json
import base64
from PIL import Image
import io
from datetime import datetime
import os
import hashlib
import threading
from config.settings import GENERATED_IMAGES_DIR, IMAGE_GENERATION_CONFIG

class ImageService:
    def __init__(self, aws_service, mongo_service):
        self.aws_service = aws_service
        self.mongo_service = mongo_service
        os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)

    def get_image_hash(self, name):
        return hashlib.md5(name.encode()).hexdigest()

    def generate_food_image_async(self, name, result):
        try:
            request_body = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": f"Professional food photography of {name}, on a clean plate, white background, high quality, 4k, detailed"
                },
                "imageGenerationConfig": IMAGE_GENERATION_CONFIG
            }
            
            response = self.aws_service.bedrock_runtime.invoke_model(
                modelId='amazon.titan-image-generator-v1',
                body=json.dumps(request_body).encode('utf-8'),
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            base64_image = response_body.get("images")[0]
            image_bytes = base64.b64decode(base64_image)
            
            image = Image.open(io.BytesIO(image_bytes))
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.get_image_hash(name)}_{timestamp}.png"
            filepath = os.path.join(GENERATED_IMAGES_DIR, filename)
            
            image = image.convert('RGB')
            image.save(filepath, optimize=True, quality=85)
            
            image_url = f"/static/generated_images/{filename}?t={timestamp}"
            result['image_url'] = image_url
            
        except Exception as e:
            print(f"Image generation error: {e}")
            result['image_url'] = None