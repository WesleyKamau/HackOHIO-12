# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
import uuid  # For generating unique message IDs
from config import Config
from pymongo import MongoClient

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

GROUPME_API_URL = 'https://api.groupme.com/v3'

# Load buildings data
with open("buildings.json", 'r') as f:
    buildings_data = json.load(f)

# MongoDB setup
client = MongoClient(app.config['MONGODB_URI'])
db = client[app.config['MONGODB_DB']]
chats_collection = db['chats']

# Endpoint to add a floor chat
@app.route('/api/chats/add', methods=['POST'])
def add_floor_chat():
    data = request.json
    groupme_link = data.get('groupme_link')
    building_id = data.get('building_id')
    floor_number = data.get('floor_number')

    if not (groupme_link and building_id and floor_number is not None):
        return jsonify({'error': 'Missing groupme_link, building_id, or floor_number'}), 400

    # Extract group_id and share_token from the GroupMe link
    group_info = extract_group_id_and_token_from_link(groupme_link)
    if not group_info:
        return jsonify({'error': 'Invalid GroupMe link'}), 400

    group_id, share_token = group_info

    print(f'Group ID: {group_id}, Share Token: {share_token}')

    # Check if the chat already exists in the database
    existing_chat = chats_collection.find_one({'groupme_id': group_id})
    if existing_chat:
        print("GroupMe ID already exists in the database.")
        return jsonify({'error': 'Chat already exists'}), 400

    # Join the group using the GroupMe API
    joined = join_group(group_id, share_token)
    if not joined:
        return jsonify({'error': 'Failed to join the GroupMe group'}), 500

    # Add the chat to the database
    chat = add_chat(group_id, building_id, floor_number)
    if chat is None:
        return jsonify({'error': 'Failed to add chat'}), 500

    return jsonify({'message': 'Chat added successfully', 'chat': chat}), 200

# Endpoint to send messages to chats based on building IDs or regions
@app.route('/api/messages/send', methods=['POST'])
def send_messages():
    # Access form data
    building_ids = request.form.getlist('building_ids')
    message_body = request.form.get('message_body')
    image_file = request.files.get('image_file')
    regions = request.form.getlist('regions')

    if not (building_ids or regions) or not message_body:
        return jsonify({'error': 'Missing building_ids or regions, or message_body'}), 400

    # Determine building_ids based on regions or provided list
    if building_ids:
        # Ensure building_ids is a list of integers
        building_ids = [int(bid) for bid in building_ids]
    else:
        # Handle regions selection
        if 'all' in regions:
            # Use all building IDs
            building_ids = [building['id'] for building in buildings_data]
        else:
            # Get building IDs for the specified regions
            building_ids = [building['id'] for building in buildings_data if building['region'] in regions]
            if not building_ids:
                return jsonify({'error': f'No buildings found in regions {regions}'}), 400

    # Retrieve groupme_ids from the database based on building_ids
    groupme_ids = get_groupme_ids_by_buildings(building_ids)

    if not groupme_ids:
        return jsonify({'error': 'No group chats found for the provided building IDs'}), 404

    # If an image file is provided, upload it to GroupMe Image Service
    image_url = None
    if image_file:
        image_url = upload_image_to_groupme(image_file)
        if not image_url:
            return jsonify({'error': 'Failed to upload image to GroupMe'}), 500

    # Send the message to each groupme chat
    for group_id in groupme_ids:
        send_message_to_group(group_id, message_body, image_url)

    return jsonify({'message': 'Messages sent successfully'}), 200

def upload_image_to_groupme(image_file):
    url = 'https://image.groupme.com/pictures'
    headers = {
        'X-Access-Token': app.config['GROUPME_ACCESS_TOKEN'],
        'Content-Type': image_file.content_type  # Use the uploaded file's content type
    }
    response = requests.post(url, headers=headers, data=image_file.read())
    if response.status_code == 200:
        response_json = response.json()
        return response_json.get('payload', {}).get('picture_url')
    else:
        print(f'Failed to upload image: {response.status_code}, {response.text}')
        return None

# Helper function to extract group_id and share_token from GroupMe link
def extract_group_id_and_token_from_link(link):
    # Example link: https://groupme.com/join_group/12345678/SHARE_TOKEN
    try:
        parts = link.strip('/').split('/')
        index = parts.index('join_group')
        group_id = parts[index + 1]
        share_token = parts[index + 2]
        return group_id, share_token
    except (ValueError, IndexError):
        return None

# Helper function to join a group using the GroupMe API
def join_group(group_id, share_token):
    url = f'{GROUPME_API_URL}/groups/{group_id}/join/{share_token}'
    params = {'token': app.config['GROUPME_ACCESS_TOKEN']}
    response = requests.post(url, params=params)
    positive_response_codes = [200, 201]
    print( app.config['GROUPME_ACCESS_TOKEN'])
    if response.status_code in positive_response_codes:
        response_json = response.json()
        print(f'Successfully joined group {group_id}')
        return True
    else:
        print(f'Failed to join group {group_id}: {response.status_code}, {response.text}')
        return False

# Helper function to add a chat to the database
def add_chat(groupme_id, building_id, floor_number):
    chat = {
        'groupme_id': groupme_id,
        'building_id': building_id,
        'floor_number': floor_number
    }
    result = chats_collection.insert_one(chat)
    if result.inserted_id:
        chat['_id'] = str(result.inserted_id)
        print(f"Chat added to database: {chat}")
        return chat
    else:
        print("Failed to insert chat into the database.")
        return None

# Helper function to get groupme_ids by building IDs
def get_groupme_ids_by_buildings(building_ids):
    groupme_ids = []
    chats = chats_collection.find({'building_id': {'$in': building_ids}})
    for chat in chats:
        groupme_ids.append(chat['groupme_id'])
    return groupme_ids

# Function to send a message directly to a GroupMe group
def send_message_to_group(group_id, text, image_url=None):
    url = f'{GROUPME_API_URL}/groups/{group_id}/messages'
    params = {'token': app.config['GROUPME_ACCESS_TOKEN']}
    message_data = {
        'message': {
            'source_guid': str(uuid.uuid4()),
            'text': text,
        }
    }
    if image_url:
        message_data['message']['attachments'] = [
            {
                'type': 'image',
                'url': image_url
            }
        ]
    response = requests.post(url, params=params, json=message_data)
    if response.status_code != 201:
        print(f'Failed to send message to group {group_id}: {response.status_code}, {response.text}')

if __name__ == '__main__':
    app.run(debug=True)
