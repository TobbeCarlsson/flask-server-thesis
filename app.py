from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
import json
import signal
import sys

app = Flask(__name__)
CORS(app)

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
            behaviors.update(json.load(f))
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
    profile = data.get("profile")
    if not profile:
        return jsonify({"error": "Missing 'profile' field"}), 400

    behavior = create_behavior(data)

    if profile not in behaviors:
        behaviors[profile] = {}

    behaviors[profile][behavior["id"]] = behavior
    save_behaviors_to_file()
    return jsonify({"status": "success", "id": behavior["id"]})


@app.route("/get_all", methods=["GET"])
def get_all_behaviors():
    profile = request.args.get("profile")
    if not profile:
        return jsonify({"error": "Missing 'profile' parameter"}), 400

    if profile not in behaviors:
        return jsonify([])

    return jsonify(list(behaviors[profile].values()))


@app.route("/mark_used", methods=["POST"])
def mark_used():
    data = request.get_json()
    profile = data.get("profile")
    used_ids = data.get("used_ids", [])

    if not profile or profile not in behaviors:
        return jsonify({"error": "Invalid or missing profile"}), 400

    for b in behaviors[profile].values():
        if b["id"] in used_ids:
            b["unusedGenerations"] = 0
        else:
            b["unusedGenerations"] += 1

    # Delete unused behaviors
    to_delete = [bid for bid, b in behaviors[profile].items() if b["unusedGenerations"] >= GENERATION_LIMIT]
