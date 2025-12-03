from flask import Flask, request, jsonify
from flask_cors import CORS
from rembg import remove
import base64
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "message": "Background Remover API Running!",
        "status": "success",
        "docs": "/remove-background"
    })

@app.route('/remove-background', methods=['POST', 'OPTIONS'])
def remove_background():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        input_data = None

        # File upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({"success": False, "error": "No file selected"}), 400
            input_data = file.read()
            logger.info(f"File upload: {len(input_data)} bytes")

        # Base64 upload
        elif request.is_json and request.json.get('image'):
            image_b64 = request.json['image']
            if image_b64.startswith('data:'):
                image_b64 = image_b64.split(',')[1]
            input_data = base64.b64decode(image_b64)
            logger.info(f"Base64 upload: {len(input_data)} bytes")

        elif request.form and 'image' in request.form:
            image_b64 = request.form['image']
            if image_b64.startswith('data:'):
                image_b64 = image_b64.split(',')[1]
            input_data = base64.b64decode(image_b64)

        else:
            return jsonify({"success": False, "error": "Send image as file or base64"}), 400

        # Size check (optional, 10MB limit)
        if len(input_data) > 10 * 1024 * 1024:
            return jsonify({"success": False, "error": "Image too large (max 10MB)"}), 400

        output_data = remove(input_data)
        result_b64 = base64.b64encode(output_data).decode('utf-8')

        return jsonify({
            "message": "Background Remover API Running!",
            "success": True,
            "processed_image": result_b64,
            "format": "png",
            "size_bytes": len(output_data)
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "bg-remover"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from rembg import remove
# import base64
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# CORS(app)

# @app.route('/')
# def home():
#     return jsonify({
#         "message": "Hello World!",
#         "status": "success",
#         "service": "Render Test Server"
#     })

# @app.route('/remove-background', methods=['POST', 'OPTIONS'])
# def remove_background():
#     if request.method == 'OPTIONS':
#         return '', 200

#     try:
#         input_data = None

#         # File upload
#         if request.files and 'image' in request.files:
#             file = request.files['image']
#             if file.filename == '':
#                 return jsonify({"success": False, "error": "No file selected"}), 400
#             input_data = file.read()
#             logger.info(f"Received file: {len(input_data)} bytes")

#         # Base64 upload
#         elif request.form and 'image' in request.form:
#             image_data = request.form['image']
#             if image_data.startswith('data:'):
#                 image_data = image_data.split(',')[1]
#             input_data = base64.b64decode(image_data)
#             logger.info(f"Received base64: {len(input_data)} bytes")

#         else:
#             return jsonify({"success": False, "error": "No image data received"}), 400

#         output_data = remove(input_data)
#         processed_image_base64 = base64.b64encode(output_data).decode('utf-8')

#         return jsonify({
#             "success": True,
#             "message": "Background removed successfully",
#             "processed_image": processed_image_base64,
#             "format": "png"
#         })

#     except Exception as e:
#         logger.error(f"Error: {e}")
#         return jsonify({"success": False, "error": str(e)}), 500

# @app.route('/health')
# def health_check():
#     return jsonify({"status": "healthy"})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)