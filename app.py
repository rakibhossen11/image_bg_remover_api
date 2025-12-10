from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import cv2
import base64
import io

app = Flask(__name__)
CORS(app)

def remove_bg(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = np.array(image)

    # Convert to BGR for OpenCV
    bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Create mask using simple threshold
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Apply GrabCut for better accuracy
    mask_gc = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    rect = (1, 1, img.shape[1]-2, img.shape[0]-2)

    cv2.grabCut(bgr, mask_gc, rect, bgdModel, fgdModel, 3, cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask_gc == 2) | (mask_gc == 0), 0, 1).astype('uint8')
    result = img * mask2[:, :, np.newaxis]

    # Convert to PNG
    output = Image.fromarray(result)
    buf = io.BytesIO()
    output.save(buf, format="PNG")
    return buf.getvalue()


@app.route('/remove-background', methods=['POST'])
def api_remove():
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400

    file = request.files['image']
    image_bytes = file.read()

    output = remove_bg(image_bytes)

    result_b64 = base64.b64encode(output).decode('utf-8')

    return jsonify({
        "success": True,
        "image": result_b64,
        "data_uri": f"data:image/png;base64,{result_b64}"
    })


@app.route("/")
def home():
    return "Light Background Remover API Running!"


if __name__ == '__main__':
    app.run(debug=False)




# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from rembg import remove
# import base64
# import logging
# import os

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# CORS(app)

# @app.route('/')
# def home():
#     return jsonify({
#         "message": "Background Remover API Running!",
#         "status": "success",
#         "docs": "/remove-background"
#     })

# @app.route('/remove-background', methods=['POST', 'OPTIONS'])
# def remove_background():
#     if request.method == 'OPTIONS':
#         return '', 200

#     try:
#         input_data = None

#         # File upload
#         if 'image' in request.files:
#             file = request.files['image']
#             if file.filename == '':
#                 return jsonify({"success": False, "error": "No file selected"}), 400
#             input_data = file.read()
#             logger.info(f"File upload: {len(input_data)} bytes")

#         # Base64 upload
#         elif request.is_json and request.json.get('image'):
#             image_b64 = request.json['image']
#             if image_b64.startswith('data:'):
#                 image_b64 = image_b64.split(',')[1]
#             input_data = base64.b64decode(image_b64)
#             logger.info(f"Base64 upload: {len(input_data)} bytes")

#         elif request.form and 'image' in request.form:
#             image_b64 = request.form['image']
#             if image_b64.startswith('data:'):
#                 image_b64 = image_b64.split(',')[1]
#             input_data = base64.b64decode(image_b64)

#         else:
#             return jsonify({"success": False, "error": "Send image as file or base64"}), 400

#         # Size check (optional, 10MB limit)
#         if len(input_data) > 10 * 1024 * 1024:
#             return jsonify({"success": False, "error": "Image too large (max 10MB)"}), 400

#         output_data = remove(input_data)
#         result_b64 = base64.b64encode(output_data).decode('utf-8')

#         return jsonify({
#             "message": "Background Remover API Running!",
#             "success": True,
#             "processed_image": result_b64,
#             "format": "png",
#             "size_bytes": len(output_data)
#         })

#     except Exception as e:
#         logger.error(f"Error: {str(e)}")
#         return jsonify({"success": False, "error": str(e)}), 500

# @app.route('/health')
# def health():
#     return jsonify({"status": "healthy", "service": "bg-remover"})

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port, debug=False)
