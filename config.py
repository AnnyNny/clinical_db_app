# config.py
from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'dbname': os.getenv('DB_NAME'),
	'port':os.getenv('DB_PORT')
}

TABLE_NAME = os.getenv('TABLE_NAME')
MIN_MAX_VIEW = os.getenv('MIN_MAX_VIEW')
