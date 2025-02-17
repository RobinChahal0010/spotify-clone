from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Audius API ka host
HOST = "https://discoveryprovider2.audius.co"

@app.route('/trending_songs', methods=['GET'])
def get_trending_songs():
    url = f"{HOST}/v1/tracks/trending"
    response = requests.get(url)

    if response.status_code == 200:
        return jsonify(response.json())  # JSON format mein frontend ko data bhejna
    else:
        return jsonify({"error": "Failed to fetch trending songs"}), 500

if __name__ == '__main__':
    app.run(debug=True)
