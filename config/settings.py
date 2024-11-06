import os
import configparser
from pathlib import Path

# Get the directory containing settings.py
CONFIG_DIR = Path(__file__).parent

# Load configuration
config = configparser.ConfigParser()
config.read(os.path.join(CONFIG_DIR, 'config.ini'))


# MongoDB Configuration
MONGO_URI = config['mongodb']['uri']
print(MONGO_URI)
MONGO_DB_NAME = config['mongodb']['db_name']
MONGO_COLLECTION_RECIPES = config['mongodb']['recipes_collection']
MONGO_COLLECTION_IMAGES = config['mongodb']['images_collection']
MONGO_CONNECTION_TIMEOUT = int(config['mongodb']['connection_timeout'])
MONGO_SELECTION_TIMEOUT = int(config['mongodb']['selection_timeout'])

# AWS Configuration
AWS_REGION = config['aws']['region']

AWS_SERVICE_NAME = config['aws']['service_name']
CLAUDE_MODEL = config['aws']['claude_model']
TITAN_MODEL = config['aws']['titan_model']

# Model Configuration
MODEL_NAME = config['model']['name']
MODEL_MAX_LENGTH = int(config['model']['max_length'])

# Flask Configuration
PORT = int(os.getenv('PORT', config['flask']['port']))
DEBUG = config['flask'].getboolean('debug')

# Image Generation Configuration
IMAGE_GENERATION_CONFIG = {
    "height": int(config['image']['height']),
    "width": int(config['image']['width']),
    "cfgScale": float(config['image']['cfg_scale']),
    "seed": int(config['image']['seed'])
}

IMAGE_QUALITY = int(config['image']['quality'])
IMAGE_FORMAT = config['image']['format']

# File Paths
BASE_DIR = Path(__file__).parent.parent
GENERATED_IMAGES_DIR = BASE_DIR / 'static' / 'generated_images'

# Ensure required directories exist
GENERATED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)