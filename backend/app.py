from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Dictionary mapping group names or identifiers to their respective GroupMe bot IDs
GROUPME_BOT_IDS = {
    "group1": "YOUR_GROUPME_BOT_ID_1",
    "group2": "YOUR_GROUPME_BOT_ID_2",
    "group3": "YOUR_GROUPME_BOT_ID_3"
}

GROUPME_API_URL = "https://api.groupme.com/v3/bots/post"


def send_groupme_message(bot_id, text):
    """
    Send a message to a GroupMe server using its bot ID.
    """
    data = {
        "bot_id": bot_id,
        "text": text
    }
    response = requests.post(GROUPME_API_URL, json=data)
    return response.status_code == 202  # 202 Accepted means message was sent successfully


@app.route('/send_message', methods=['POST'])
def send_message():
    """
    Endpoint to send a message to a list of GroupMe servers based on a provided query.
    Request format: JSON with 'query' and 'message'.
    """
    data = request.get_json()

    query = data.get('query', None)
    message = data.get('message', None)

    if not query or not message:
        return jsonify({"error": "Query and message are required"}), 400

    # Find the bot IDs that match the query
    matched_groups = [group for group in GROUPME_BOT_IDS if query in group]

    if not matched_groups:
        return jsonify({"error": "No matching group found"}), 404

    # Send the message to each matched group
    results = {}
    for group in matched_groups:
        bot_id = GROUPME_BOT_IDS[group]
        success = send_groupme_message(bot_id, message)
        results[group] = "Message sent" if success else "Failed to send message"

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(debug=True)
