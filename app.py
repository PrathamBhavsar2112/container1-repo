from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

PERSISTENT_VOLUME_PATH = "/pratham_PV_dir/"
CONTAINER2_URL = "http://container2:5000/calculate"

@app.route("/store-file", methods=["POST"])
def store_file():
    data = request.get_json()
    if not data or "file" not in data or "data" not in data:
        return jsonify({"file": None, "error": "Invalid JSON input."}), 400

    file_name = data["file"]
    file_content = data["data"]
    file_path = os.path.join(PERSISTENT_VOLUME_PATH, file_name)

    try:
        os.makedirs(PERSISTENT_VOLUME_PATH, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(file_content)
        return jsonify({"file": file_name, "message": "Success."}), 200
    except Exception:
        return jsonify({"file": file_name, "error": "Error while storing the file to the storage."}), 500

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    if not data or "file" not in data or "product" not in data:
        return jsonify({"file": None, "error": "Invalid JSON input."}), 400

    file_name = data["file"]
    product = data["product"]
    payload = {"file": file_name, "product": product}

    try:
        response = requests.post(CONTAINER2_URL, json=payload, timeout=5)
        return response.json(), response.status_code
    except requests.exceptions.RequestException:
        # Simplified: Let Container 2 handle most errors, fallback to generic error
        return jsonify({"file": file_name, "error": "Container 2 is unreachable."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)