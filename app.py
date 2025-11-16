from flask import Flask, request, jsonify
from flask_cors import CORS
from rembg import remove
import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "message": "Hello World!",
        "status": "success",
        "service": "Render Test Server"
    })

@app.route('/remove-background', methods=['POST', 'OPTIONS'])
def remove_background():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        input_data = None

        # File upload
        if request.files and 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({"success": False, "error": "No file selected"}), 400
            input_data = file.read()
            logger.info(f"Received file: {len(input_data)} bytes")

        # Base64 upload
        elif request.form and 'image' in request.form:
            image_data = request.form['image']
            if image_data.startswith('data:'):
                image_data = image_data.split(',')[1]
            input_data = base64.b64decode(image_data)
            logger.info(f"Received base64: {len(input_data)} bytes")

        else:
            return jsonify({"success": False, "error": "No image data received"}), 400

        output_data = remove(input_data)
        processed_image_base64 = base64.b64encode(output_data).decode('utf-8')

        return jsonify({
            "success": True,
            "message": "Background removed successfully",
            "processed_image": processed_image_base64,
            "format": "png"
        })

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)