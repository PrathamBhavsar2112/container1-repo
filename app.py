from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

PERSISTENT_VOLUME_PATH = "/pratham_PV_dir/"
CONTAINER2_URL = "http://container2:5000/calculate"

@app.route("/store-file", methods=["POST"])
def store_file():
    try:
        data = request.get_json()
        
        # ✅ Fix 1: Ensure file and data keys exist
        if not data or "file" not in data or "data" not in data:
            return jsonify({"file": None, "error": "Invalid JSON input."}), 400

        file_name = data["file"]
        file_content = data["data"].replace(" ", "")  # ✅ Fix 2: Remove extra spaces

        os.makedirs(PERSISTENT_VOLUME_PATH, exist_ok=True)
        file_path = os.path.join(PERSISTENT_VOLUME_PATH, file_name)
        with open(file_path, "w") as f:
            f.write(file_content)

        return jsonify({"file": file_name, "message": "Success."}), 200

    except Exception:
        return jsonify({"file": None, "error": "Error while storing the file to the storage."}), 500


@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()

        # ✅ Fix 3: Ensure required keys exist
        if not data or "file" not in data or "product" not in data:
            return jsonify({"file": None, "error": "Invalid JSON input."}), 400

        file_name = data["file"]
        product_name = data["product"]
        file_path = os.path.join(PERSISTENT_VOLUME_PATH, file_name)

        # ✅ Fix 4: Check if file exists first
        if not os.path.exists(file_path):
            return jsonify({"file": file_name, "error": "File not found."}), 404

        payload = {"file": file_name, "product": product_name}
        try:
            response = requests.post(CONTAINER2_URL, json=payload, timeout=10)
            response.raise_for_status()
            return response.json(), response.status_code

        except requests.exceptions.Timeout:
            return jsonify({"file": file_name, "error": "Container 2 request timed out."}), 500

        except requests.exceptions.RequestException:
            return jsonify({"file": file_name, "error": "Container 2 is unreachable."}), 500

    except Exception:
        return jsonify({"file": None, "error": "Invalid JSON input."}), 400  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=False)
