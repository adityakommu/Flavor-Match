import torch
from transformers import AutoTokenizer, AutoModel
from config.settings import MODEL_NAME

class ModelService:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModel.from_pretrained(MODEL_NAME).to(self.device)
        self.model.eval()

    def process_food_data(self, extracted_info):
        try:
            # Parse food data
            if isinstance(extracted_info, list) and len(extracted_info) > 0:
                if isinstance(extracted_info[0], dict) and 'text' in extracted_info[0]:
                    food_data = json.loads(extracted_info[0]['text'])
                else:
                    food_data = extracted_info[0]
            else:
                return None

            # Process ingredients
            ingredients = food_data.get('INGREDIENTS', [])
            ingredients_text = " ".join(ingredients)
                
            # Tokenize
            encoded = self.tokenizer(
                ingredients_text,
                padding=True,
                truncation=True,
                return_tensors='pt',
                max_length=128
            ).to(self.device)
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**encoded)
                embedding = outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy().tolist()
            
            # Clear GPU memory
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
                
            return embedding
            
        except Exception as e:
            print(f"Error in process_food_data: {e}")
            return None

    def __del__(self):
        # Clean up GPU memory
        if hasattr(self, 'model'):
            del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()