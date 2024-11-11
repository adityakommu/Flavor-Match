def clean_json_string(json_str):
    """Clean and format JSON string properly"""
    json_str = json_str.replace("'", '"')
    json_str = ' '.join(json_str.split())
    return json_str

def detect_diet_type(query, info_dict):
    """Detect diet type from query and info dictionary"""
    diet_type = info_dict.get('Diet', 'Vegetarian')
    
    non_veg_ingredients = [
        'chicken', 'meat', 'beef', 'pork', 'fish', 'mutton', 
        'lamb', 'seafood', 'shrimp', 'prawn'
    ]
    
    if any(ingredient in query.lower() for ingredient in non_veg_ingredients):
        diet_type = 'Non Vegetarian'
        
    return diet_type