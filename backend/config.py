# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    GROUPME_ACCESS_TOKEN = os.environ.get('GROUPME_ACCESS_TOKEN')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    ADMIN_PASSWORD = os.environ.get('EXECUTIVE_PASSWORD', 'exec_password')
    MONGODB_URI = os.environ.get('MONGODB_URI')
    MONGODB_DB = str(os.environ.get('MONGODB_DB'))
    # Removed BOT_USER_ID and BOT_NAME as they are no longer needed
