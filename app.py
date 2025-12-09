from flask import Flask, request, jsonify
from flask_cors import CORS
from rembg import remove, new_session
from PIL import Image
import base64
import logging
import os
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

MAX_IMAGE_SIZE = (720, 720)
MAX_UPLOAD_MB = 5

# ----------------------------
# FIX: Load model manually
# ----------------------------
MODEL_PATH = "/app/models/u2netp.onnx"   # <-- CHANGE to your server path

if not os.path.exists(MODEL_PATH):
    logger.error("MODEL FILE NOT FOUND! Background remove will NOT work.")

logger.info(f"Loading rembg model from: {MODEL_PATH}")
session = new_session(
    model=MODEL_PATH,
    providers=["CPUExecutionProvider"]
)
logger.info("Model loaded successfully!")


def compress_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail(MAX_IMAGE_SIZE)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70, optimize=True)
    buf.seek(0)
    return buf.getvalue()


@app.route("/remove-background", methods=["POST"])
def remove_bg():

    try:
        image_bytes = None

        if "image" in request.files:
            image_bytes = request.files["image"].read()

        elif request.is_json and request.json.get("image"):
            b64 = request.json["image"]
            if "data:" in b64:
                b64 = b64.split(",")[1]
            image_bytes = base64.b64decode(b64)

        else:
            return jsonify({"success": False, "error": "No image provided"}), 400

        image_bytes = compress_image(image_bytes)

        # FIX: apply model here
        output = remove(image_bytes, session=session)

        result_b64 = base64.b64encode(output).decode("utf-8")

        return jsonify({
            "success": True,
            "image": result_b64,
            "data_uri": f"data:image/png;base64,{result_b64}",
        })

    except Exception as e:
        logger.error(str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/")
def home():
    return "Background Remover Working with Local Model"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)



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
