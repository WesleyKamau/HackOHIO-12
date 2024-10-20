# models.py

# Mock database for chats and buildings
chats_db = []

def add_chat(groupme_id, building_id, floor_number):
    # Check if the groupme_id already exists in chats_db
    for chat in chats_db:
        if chat['groupme_id'] == groupme_id:
            print("GroupMe ID already exists in the database.")
            return None  # Optionally, return an error message or raise an exception
    
    # If groupme_id doesn't exist, add the new chat
    chat = {
        'groupme_id': groupme_id,
        'building_id': building_id,
        'floor_number': floor_number
    }
    chats_db.append(chat)
    print(chats_db)
    return chat


def get_group_ids_by_buildings(building_ids):
    group_ids = []
    for chat in chats_db:
        if chat['building_id'] in building_ids:
            group_ids.append(chat['groupme_id'])
    return group_ids

def get_group_ids_by_region(region):
    building_ids = [b['building_id'] for b in buildings_db if b['region'] == region]
    return get_group_ids_by_buildings(building_ids)

def get_all_buildings():
    return buildings_db
