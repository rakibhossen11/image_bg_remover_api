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
def hello_world():
    return 'Hello, World!'

@app.route('/remove-background', methods=['POST', 'OPTIONS'])
def remove_background():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        input_data = None
        
        # Check for file upload
        if request.files and 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({"success": False, "error": "No file selected"}), 400
            
            input_data = file.read()
            logger.info(f"Received file: {len(input_data)} bytes")
            
        # Check for base64 data
        elif request.form and 'image' in request.form:
            image_data = request.form['image']
            if image_data.startswith('data:'):
                image_data = image_data.split(',')[1]
            input_data = base64.b64decode(image_data)
            logger.info(f"Received base64: {len(input_data)} bytes")
            
        else:
            return jsonify({"success": False, "error": "No image data received"}), 400

        if not input_data or len(input_data) == 0:
            return jsonify({"success": False, "error": "Empty image data"}), 400

        # Process image
        output_data = remove(input_data)
        processed_image_base64 = base64.b64encode(output_data).decode('utf-8')

        return jsonify({
            "success": True,
            "message": "Background removed successfully",
            "processed_image": processed_image_base64,
            "format": "png"
        })
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return jsonify({"success": False, "error": f"Processing failed: {str(e)}"}), 500

@app.route('/test', methods=['POST'])
def test_endpoint():
    return jsonify({
        "success": True,
        "message": "Server is working",
        "content_type": request.content_type
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)