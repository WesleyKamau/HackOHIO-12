from pymongo import MongoClient
from config import Config
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config.from_object(Config)

try:
    MONGODB_URI = app.config['MONGODB_URI']
    print(f"Connecting to MongoDB: {MONGODB_URI}")
    client = MongoClient(MONGODB_URI)
    client.admin.command('ping')
    print("Connected to MongoDB!")
except Exception as e:
    print(f"Connection failed: {e}")
