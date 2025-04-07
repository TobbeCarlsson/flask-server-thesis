from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
import json
import signal
import sys
app = Flask(__name__)
CORS(app)  # Allow requests from Unity WebGL

# In-memory "database"
behaviors = {}
GENERATION_LIMIT = 5

BEHAVIORS_FILE = os.path.join(os.path.dirname(__file__), 'behaviors.json')


def save_behaviors_to_file():
    with open(BEHAVIORS_FILE, 'w') as f:
        json.dump(behaviors, f)

def load_behaviors_from_file():
    global behaviors
    if os.path.exists(BEHAVIORS_FILE):
        with open(BEHAVIORS_FILE, 'r') as f:
            behaviors = json.load(f)
    else:
        behaviors = {}


def create_behavior(data):
    return {
        "id": data.get("id"),
        "smallDetectionRadius": data.get("smallDetectionRadius"),
        "largeDetectionRadius": data.get("largeDetectionRadius"),
        "fullStopRadius": data.get("fullStopRadius"),
        "detectionAngle": data.get("detectionAngle"),
        "baseSpeed": data.get("baseSpeed"),
        "playerEncounteredSpeed": data.get("playerEncounteredSpeed"),
        "stopDuration": data.get("stopDuration"),
        "turnAfterStopAngle": data.get("turnAfterStopAngle"),
        "randomTurnLowerBound": data.get("randomTurnLowerBound"),
        "randomTurnUpperBound": data.get("randomTurnUpperBound"),
        "randomnessFactor": data.get("randomnessFactor"),
        "baseTurnAngle": data.get("baseTurnAngle"),
        "turnAngleRandomness": data.get("turnAngleRandomness"),
        "turnSpeed": data.get("turnSpeed"),
        "unusedGenerations": 0
    }


@app.route("/upload", methods=["POST"])
def upload_behavior():
    data = request.get_json()
    behavior = create_behavior(data)
    behaviors[behavior["id"]] = behavior
    save_behaviors_to_file()
    return jsonify({"status": "success", "id": behavior["id"]})


@app.route("/get_all", methods=["GET"])
def get_all_behaviors():
    return jsonify(list(behaviors.values()))


@app.route("/mark_used", methods=["POST"])
def mark_used():
    used_ids = request.json.get("used_ids", [])
    for b in behaviors.values():
        if b["id"] in used_ids:
            b["unusedGenerations"] = 0
        else:
            b["unusedGenerations"] += 1

    # Delete unused behaviors
    to_delete = [bid for bid, b in behaviors.items() if b["unusedGenerations"] >= GENERATION_LIMIT]
    for bid in to_delete:
        del behaviors[bid]

    return jsonify({"status": "updated", "deleted": to_delete})

@app.route("/reset_unused_generations", methods=["POST"])
def reset_unused_generations():
    parent_ids = request.json.get("parent_ids", [])
    updated = []

    for pid in parent_ids:
        behavior = behaviors.get(pid)
        if behavior:
            behavior["unusedGenerations"] = 0
            updated.append(pid)

    return jsonify({"status": "success", "updated": updated})

@app.route('/get_behavior_count', methods=['GET'])
def get_behavior_count():
    behavior_count = len(behaviors)
    return jsonify({'behavior_count': behavior_count})

@app.route("/", methods=["GET"])
def health_check():
    return "Server running."


def handle_exit(sig, frame):
    save_behaviors_to_file()
    sys.exit(0)



if __name__ == "__main__":
    load_behaviors_from_file()  
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    app.run(host="0.0.0.0", port=5000)

