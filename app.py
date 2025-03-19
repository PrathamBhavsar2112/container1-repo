from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Persistent Volume path as specified in the assignment
PERSISTENT_VOLUME_PATH = "/pratham_PV_dir/"
CONTAINER2_URL = "http://container2:5000/calculate"  # Container 2 Service name in Kubernetes

@app.route("/store-file", methods=["POST"])
def store_file():
    try:
        data = request.get_json()
        if not data or "file" not in data or "data" not in data:
            return jsonify({"file": None, "error": "Invalid JSON input."}), 400

        file_name = data["file"]
        file_content = data["data"]

        # Ensure persistent volume directory exists
        os.makedirs(PERSISTENT_VOLUME_PATH, exist_ok=True)

        file_path = os.path.join(PERSISTENT_VOLUME_PATH, file_name)
        with open(file_path, "w") as f:
            f.write(file_content)

        return jsonify({"file": file_name, "message": "Success."}), 200

    except Exception:
        return jsonify({"file": file_name if 'file_name' in locals() else None, 
                        "error": "Error while storing the file to the storage."}), 500

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()
        if not data or "file" not in data or "product" not in data:
            return jsonify({"file": None, "error": "Invalid JSON input."}), 400

        file_name = data["file"]
        product_name = data["product"]

        # Check if file exists in persistent volume
        file_path = os.path.join(PERSISTENT_VOLUME_PATH, file_name)
        if not os.path.exists(file_path):
            return jsonify({"file": file_name, "error": "File not found."}), 404

        # Forward request to Container 2
        payload = {"file": file_name, "product": product_name}
        response = requests.post(CONTAINER2_URL, json=payload, timeout=10)
        response.raise_for_status()

        return response.json(), response.status_code

    except requests.exceptions.RequestException:
        return jsonify({"file": file_name if 'file_name' in locals() else None, 
                        "error": "File not found."}), 404
    except Exception:
        return jsonify({"file": file_name if 'file_name' in locals() else None, 
                        "error": "Error processing request."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=False)