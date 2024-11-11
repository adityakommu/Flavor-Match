import boto3
import json
from config.settings import AWS_REGION, AWS_SERVICE_NAME

class AWSService:
    def __init__(self):
        self.bedrock_runtime = boto3.client(
            service_name=AWS_SERVICE_NAME,
            region_name=AWS_REGION
        )

    def get_food_info(self, prompt):
        try:
            extraction_template = (
                "Given a food-related text that asks for dishes similar to a reference dish, extract the following in JSON format:\n"
                "1. DISH NAME: Always use the reference dish mentioned in the prompt\n"
                "2. INGREDIENTS: List all ingredients for the DISH NAME\n"
                "3. Cuisine: Identify the cuisine\n"
                "4. Course: Specify if Snack or Main course\n"
                "5. Diet: Indicate if Vegetarian or Non Vegetarian\n"
                "6. Generated_Description: Describe the dish and mention similar dishes\n"
            )
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": f"System:{extraction_template}\n\nHuman:{prompt}\n\nAssistant:"
                    }
                ]
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps(request_body)
            )
            
            if response and 'body' in response:
                response_body = json.loads(response['body'].read().decode('utf-8'))
                if 'content' in response_body:
                    for content_item in response_body['content']:
                        if content_item.get('type') == 'text':
                            text_content = content_item.get('text', '')
                            json_start = text_content.find('{')
                            json_end = text_content.rfind('}') + 1
                            if json_start >= 0 and json_end > json_start:
                                json_str = text_content[json_start:json_end]
                                food_data = json.loads(json_str)
                                return [{"text": json.dumps(food_data)}]
            
            return None
                
        except Exception as e:
            print(f"Error in get_food_info: {e}")
            return None