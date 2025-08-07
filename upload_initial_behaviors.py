import json
import requests

# Path to your local JSON file
FILE_PATH = 'initial_behaviors.json'

# Server URL (adjust if hosted elsewhere)
UPLOAD_URL = 'https://flask-server-thesis-ssa7.onrender.com/upload'

# Load behaviors from file
with open(FILE_PATH, 'r') as f:
    data = json.load(f)

profile_name = 'initial'
behaviors = data.get(profile_name, {})

# Upload each behavior
for behavior_id, behavior in behaviors.items():
    # Ensure the profile field is included
    behavior['profile'] = profile_name

    response = requests.post(UPLOAD_URL, json=behavior)

    if response.status_code == 200:
        print(f"✅ Uploaded behavior {behavior_id}")
    else:
        print(f"❌ Failed to upload {behavior_id}: {response.status_code} - {response.text}")
