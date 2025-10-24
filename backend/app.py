# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import uuid  # For generating unique message IDs
import logging
from config import Config
from pymongo import MongoClient, errors as pymongo_errors

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Module-level defaults so module can be imported without side-effects
GROUPME_API_URL = 'https://api.groupme.com/v3'
buildings_data = []
chats_collection = None
_fallback_chats = []


def init_app():
    """Perform application initialization that should only run in the main process.

    This moves environment validation, config load, CORS, buildings file load,
    and MongoDB connection out of import-time execution so the module can be
    imported safely (for testing, linting, or use with WSGI servers).
    """
    global buildings_data, chats_collection, _fallback_chats

    # Validate and load configuration (warning-only in dev, raises in prod if enabled)
    try:
        Config.validate(fail_on_missing=False)
    except Exception:
        logger.exception("Configuration validation raised an exception")

    app.config.from_object(Config)
    # Ensure an application-level environment and computed DB name are available
    # Use a distinct key 'APP_ENV' to avoid colliding with Flask's internal 'ENV'
    app_env = getattr(Config, 'ENV', 'dev')
    app.config['APP_ENV'] = app_env
    # Compute the DB name using the helper added to Config
    try:
        app.config['MONGODB_DB_NAME'] = Config.MONGODB_DB_NAME()
    except Exception:
        # Fall back gracefully if method is missing for older installs
        app.config['MONGODB_DB_NAME'] = app.config.get('MONGODB_DB', 'rhac_db')
    CORS(app)

    # Load buildings data safely
    try:
        with open("buildings.json", 'r', encoding='utf-8') as f:
            buildings_data = json.load(f)
    except FileNotFoundError:
        logger.warning("buildings.json not found; using empty buildings list")
        buildings_data = []
    except json.JSONDecodeError as e:
        logger.error("Failed to parse buildings.json: %s", e)
        buildings_data = []

    # MongoDB setup with safe fallbacks
    chats_collection = None
    _fallback_chats = []
    if app.config.get('MONGODB_URI'):
        try:
            client = MongoClient(app.config['MONGODB_URI'], serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            dbname = app.config.get('MONGODB_DB_NAME') or app.config.get('MONGODB_DB') or 'rhac_db'
            db = client[dbname]
            chats_collection = db['chats']
            logger.info("Connected to MongoDB: %s (env=%s)", dbname, app.config.get('APP_ENV'))
        except pymongo_errors.PyMongoError:
            logger.exception("Failed to connect to MongoDB; falling back to in-memory storage")
            chats_collection = None
            _fallback_chats = []
    else:
        logger.warning("MONGODB_URI not set; using in-memory fallback storage for chats")


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

    # Check if the chat already exists in the database or fallback storage
    if chats_collection is not None:
        # Only consider chats for the active environment
        existing_chat = chats_collection.find_one({'groupme_id': group_id, 'env': app.config.get('APP_ENV')})
    else:
        existing_chat = next((c for c in _fallback_chats if c['groupme_id'] == group_id and c.get('env') == app.config.get('APP_ENV')), None)

    if existing_chat:
        logger.info("GroupMe ID already exists in storage: %s", group_id)
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

    # Validate executive/admin password server-side
    password = request.form.get('password') or request.form.get('auth')
    if not password or password != app.config.get('ADMIN_PASSWORD'):
        logger.warning("Unauthorized send_messages attempt")
        return jsonify({'error': 'Unauthorized'}), 401

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

    # Map building_id -> groupme_ids
    group_map = get_groupme_map_by_buildings(building_ids)

    # If no group chats found for any building, return 404
    total_groups = sum(len(v) for v in group_map.values())
    if total_groups == 0:
        return jsonify({'error': 'No group chats found for the provided building IDs'}), 404

    # If an image file is provided, upload it to GroupMe Image Service
    image_url = None
    if image_file:
        image_url = upload_image_to_groupme(image_file)
        if not image_url:
            return jsonify({'error': 'Failed to upload image to GroupMe'}), 500

    # Send messages grouped by building and collect results per building
    per_building_results = []
    overall_successes = 0
    overall_failures = 0

    # Build a quick lookup for building names
    building_lookup = {b['id']: b.get('name', '') for b in buildings_data}

    for bid, group_entries in group_map.items():
        # Each group entry may be a dict with group_id and floor_number (new structure),
        # or a plain group id string for backward compatibility.
        building_entry = {'building_id': bid, 'building_name': building_lookup.get(bid, ''), 'results': []}
        for g in group_entries:
            if isinstance(g, dict):
                gid = g.get('group_id')
                floor_number = g.get('floor_number')
            else:
                gid = g
                floor_number = None

            res = send_message_to_group(gid, message_body, image_url)
            entry = {
                'group_id': gid,
                'floor_number': floor_number,
                'success': bool(res.get('success')),
                'status_code': res.get('status_code'),
                'error': res.get('error'),
            }
            building_entry['results'].append(entry)
            if entry['success']:
                overall_successes += 1
            else:
                overall_failures += 1

        per_building_results.append(building_entry)

    total = overall_successes + overall_failures
    if total == 0:
        return jsonify({'message': 'No group chats found', 'per_building': per_building_results}), 404

    if overall_failures == 0:
        return jsonify({'message': 'All messages sent successfully', 'per_building': per_building_results}), 200
    elif overall_successes > 0:
        return jsonify({
            'message': 'Some messages were sent successfully',
            'summary': {'total': total, 'sent': overall_successes, 'failed': overall_failures},
            'per_building': per_building_results,
        }), 207
    else:
        return jsonify({'message': 'No messages were sent', 'per_building': per_building_results}), 502


@app.route('/api/buildings', methods=['GET'])
def get_buildings():
    return jsonify({'buildings': buildings_data}), 200


@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.get_json() or {}
    password = data.get('password') or request.form.get('password')
    if not password:
        return jsonify({'error': 'Missing password'}), 400
    if password == app.config.get('ADMIN_PASSWORD'):
        return jsonify({'message': 'Authenticated'}), 200
    else:
        return jsonify({'error': 'Unauthorized'}), 401

def upload_image_to_groupme(image_file):
    url = 'https://image.groupme.com/pictures'
    headers = {
        'X-Access-Token': app.config.get('GROUPME_ACCESS_TOKEN'),
        'Content-Type': image_file.content_type  # Use the uploaded file's content type
    }

    if not headers['X-Access-Token']:
        logger.error("GROUPME_ACCESS_TOKEN not configured; cannot upload image")
        return None

    try:
        response = requests.post(url, headers=headers, data=image_file.read(), timeout=10)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get('payload', {}).get('picture_url')
    except requests.RequestException as e:
        logger.exception("Failed to upload image to GroupMe: %s", e)
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
    token = app.config.get('GROUPME_ACCESS_TOKEN')
    if not token:
        logger.error("GROUPME_ACCESS_TOKEN is not set; cannot join group %s", group_id)
        return False

    params = {'token': token}
    try:
        response = requests.post(url, params=params, timeout=10)
        if response.status_code in (200, 201):
            logger.info("Successfully joined group %s", group_id)
            return True
        else:
            logger.error("Failed to join group %s: %s %s", group_id, response.status_code, response.text)
            return False
    except requests.RequestException:
        logger.exception("Network error while joining group %s", group_id)
        return False

# Helper function to add a chat to the database
def add_chat(groupme_id, building_id, floor_number):
    chat = {
        'groupme_id': groupme_id,
        'building_id': building_id,
        'floor_number': floor_number,
        # Tag the chat with the application environment to avoid mixing dev/prod data
        'env': app.config.get('APP_ENV')
    }
    if chats_collection is not None:
        try:
            result = chats_collection.insert_one(chat)
            if result.inserted_id:
                chat['_id'] = str(result.inserted_id)
                logger.info("Chat added to database: %s", chat)
                return chat
        except Exception:
            logger.exception("Failed to insert chat into MongoDB")
            return None
    else:
        # Fallback in-memory storage (development / offline mode)
        _fallback_chats.append(chat)
        logger.info("Chat added to in-memory storage: %s", chat)
        return chat


# Helper function to get groupme_ids by building IDs
def get_groupme_ids_by_buildings(building_ids):
    groupme_ids = []
    if chats_collection is not None:
        try:
            # Filter by active environment
            chats = chats_collection.find({'building_id': {'$in': building_ids}, 'env': app.config.get('APP_ENV')})
            for chat in chats:
                groupme_ids.append(chat['groupme_id'])
        except Exception:
            logger.exception("Error querying chats from MongoDB; returning empty list")
            return []
    else:
        groupme_ids = [c['groupme_id'] for c in _fallback_chats if c.get('building_id') in building_ids and c.get('env') == app.config.get('APP_ENV')]

    return groupme_ids


def get_groupme_map_by_buildings(building_ids):
    """Return a mapping of building_id -> list of group entries.

    Each entry is a dict with keys:
      - 'group_id' (str)
      - 'floor_number' (int|None)

    This preserves backward compatibility (values may still be plain group_id strings
    when older code populates the structure), but new code will return rich entries.
    """
    mapping = {bid: [] for bid in building_ids}
    if chats_collection is not None:
        try:
            # Filter by the active application environment
            chats = chats_collection.find({'building_id': {'$in': building_ids}, 'env': app.config.get('APP_ENV')})
            for chat in chats:
                bid = chat.get('building_id')
                gid = chat.get('groupme_id')
                floor = chat.get('floor_number')
                if bid in mapping:
                    mapping[bid].append({'group_id': gid, 'floor_number': floor})
        except Exception:
            logger.exception("Error querying chats from MongoDB for mapping; returning empty mapping")
            return mapping
    else:
        for c in _fallback_chats:
            # Respect environment when using fallback storage
            if c.get('env') != app.config.get('APP_ENV'):
                continue
            bid = c.get('building_id')
            if bid in mapping:
                mapping[bid].append({'group_id': c.get('groupme_id'), 'floor_number': c.get('floor_number')})

    return mapping

# Function to send a message directly to a GroupMe group
def send_message_to_group(group_id, text, image_url=None):
    url = f'{GROUPME_API_URL}/groups/{group_id}/messages'
    token = app.config.get('GROUPME_ACCESS_TOKEN')
    if not token:
        logger.error("GROUPME_ACCESS_TOKEN is not set; cannot send message to %s", group_id)
        return {'success': False, 'group_id': group_id, 'status_code': None, 'error': 'GROUPME_ACCESS_TOKEN not set'}

    params = {'token': token}
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
    try:
        response = requests.post(url, params=params, json=message_data, timeout=10)
        if response.status_code != 201:
            logger.error("Failed to send message to group %s: %s %s", group_id, response.status_code, response.text)
            return {
                'success': False,
                'group_id': group_id,
                'status_code': response.status_code,
                'error': response.text,
            }
        logger.info("Message sent to group %s", group_id)
        return {'success': True, 'group_id': group_id, 'status_code': response.status_code}
    except requests.RequestException as e:
        logger.exception("Network error while sending message to group %s", group_id)
        return {'success': False, 'group_id': group_id, 'status_code': None, 'error': str(e)}

if __name__ == '__main__':
    # Configure debug mode via FLASK_DEBUG env var (truthy values enable debug)
    import os

    flask_debug_env = os.getenv('FLASK_DEBUG', '')
    debug = flask_debug_env.lower() in ('1', 'true', 'yes', 'on')

    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', '5000'))

    # Initialize app resources that should only run in the main process
    init_app()

    # Only enable the reloader when debug mode is explicitly requested
    app.run(host=host, port=port, debug=debug, use_reloader=debug)
