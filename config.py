# config.py
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'dbname': os.getenv('DB_NAME')
}

TABLE_NAME = os.getenv('TABLE_NAME')

# Other configurations
API_KEY = os.getenv('API_KEY')
DEBUG_MODE = os.getenv('DEBUG') == 'true'  # Convert to boolean
