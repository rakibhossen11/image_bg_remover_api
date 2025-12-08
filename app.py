from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import io
import base64
import logging
import urllib.request
import time

# Memory optimization
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use DISABLED MODEL for free tier
MODEL_ENABLED = False  # Turn off AI for free tier

@app.route('/')
def home():
    return jsonify({
        "service": "Background Remover API",
        "status": "running",
        "model_enabled": MODEL_ENABLED,
        "note": "Free tier - using mock processing"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "memory": "optimized",
        "model": "disabled_for_free_tier"
    })

@app.route('/remove-background', methods=['POST'])
def remove_background():
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No image"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        # Read and compress image
        image_data = file.read()
        
        if len(image_data) > 2 * 1024 * 1024:
            return jsonify({"success": False, "error": "Image too large (max 2MB)"}), 400
        
        # Mock processing - Return original image with transparency
        # In production, use actual rembg
        
        # For free tier, return the same image
        # Or use a simple Python-based background removal
        
        # Simple edge detection-based background removal
        try:
            from PIL import Image
            import numpy as np
            
            img = Image.open(io.BytesIO(image_data)).convert("RGBA")
            img_array = np.array(img)
            
            # Simple background removal (green screen effect)
            # This is a dummy implementation
            # Replace with actual logic if needed
            
            # Create alpha channel (simple threshold)
            r, g, b, a = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2], img_array[:,:,3]
            
            # Simple green screen removal (example)
            # Adjust threshold based on your needs
            mask = (g > 200) & (r < 150) & (b < 150)
            a[mask] = 0
            
            # Create new image with alpha
            result_array = np.stack([r, g, b, a], axis=-1)
            result_img = Image.fromarray(result_array, 'RGBA')
            
            # Save to buffer
            buffer = io.BytesIO()
            result_img.save(buffer, format='PNG', optimize=True)
            result_data = buffer.getvalue()
            
            result_b64 = base64.b64encode(result_data).decode('utf-8')
            
            return jsonify({
                "success": True,
                "message": "Background removed (simple algorithm)",
                "processed_image": result_b64,
                "model_used": "simple_python"
            })
            
        except ImportError:
            # If PIL/numpy not available, return original
            result_b64 = base64.b64encode(image_data).decode('utf-8')
            
            return jsonify({
                "success": True,
                "message": "Image returned as-is (no processing available)",
                "processed_image": result_b64,
                "note": "Install PIL and numpy for simple background removal"
            })
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    # Use lightweight server
    try:
        from waitress import serve
        logger.info(f"🚀 Starting lightweight server on port {port}")
        serve(app, host='0.0.0.0', port=port, threads=1)
    except ImportError:
        app.run(host='0.0.0.0', port=port, debug=False)

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from rembg import remove, new_session
# from PIL import Image
# import base64
# import logging
# import os
# import io

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# CORS(app)

# # ✅ Environment variables with defaults
# MAX_IMAGE_SIZE = (768, 768)
# MAX_UPLOAD_MB = int(os.getenv('MAX_UPLOAD_MB', '8'))
# MODEL_PATH = os.getenv('MODEL_PATH', '/home/appuser/.u2net')

# # ✅ Create models directory if it doesn't exist
# os.makedirs(MODEL_PATH, exist_ok=True)

# # ✅ Load model ONCE when app starts
# logger.info("Loading rembg model...")
# session = new_session(
#     "u2netp",
#     providers=["CPUExecutionProvider"]
# )
# logger.info("Model loaded successfully!")


# def preprocess_image(image_bytes):
#     """Resize + compress image to reduce RAM usage"""
#     try:
#         img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#         img.thumbnail(MAX_IMAGE_SIZE)
        
#         buffer = io.BytesIO()
#         img.save(buffer, format="JPEG", quality=70, optimize=True)
#         return buffer.getvalue()
#     except Exception as e:
#         logger.error(f"Preprocessing error: {e}")
#         raise


# @app.route('/')
# def home():
#     return jsonify({
#         "message": "Background Remover API Running in Docker!",
#         "status": "success",
#         "endpoints": {
#             "remove_background": "POST /remove-background",
#             "health": "GET /health"
#         },
#         "limits": {
#             "max_upload_mb": MAX_UPLOAD_MB,
#             "max_dimensions": MAX_IMAGE_SIZE
#         }
#     })


# @app.route('/remove-background', methods=['POST', 'OPTIONS'])
# def remove_background():
#     if request.method == 'OPTIONS':
#         return '', 200

#     try:
#         input_data = None

#         # ✅ File upload
#         if 'image' in request.files:
#             file = request.files['image']
#             if file.filename == '':
#                 return jsonify({"success": False, "error": "No file selected"}), 400
#             input_data = file.read()

#         # ✅ JSON Base64 upload
#         elif request.is_json and request.json.get('image'):
#             image_b64 = request.json['image']
#             if image_b64.startswith('data:'):
#                 image_b64 = image_b64.split(',')[1]
#             input_data = base64.b64decode(image_b64)

#         # ✅ Form base64 upload
#         elif request.form and 'image' in request.form:
#             image_b64 = request.form['image']
#             if image_b64.startswith('data:'):
#                 image_b64 = image_b64.split(',')[1]
#             input_data = base64.b64decode(image_b64)

#         else:
#             return jsonify({
#                 "success": False, 
#                 "error": "Send image as: file upload, JSON base64, or form base64",
#                 "examples": {
#                     "curl_file": "curl -X POST -F 'image=@photo.jpg' http://localhost:5000/remove-background",
#                     "curl_base64": "curl -X POST -H 'Content-Type: application/json' -d '{\"image\":\"base64string\"}' http://localhost:5000/remove-background"
#                 }
#             }), 400

#         logger.info(f"Original size: {len(input_data)} bytes")

#         # ✅ Upload size limit
#         if len(input_data) > MAX_UPLOAD_MB * 1024 * 1024:
#             return jsonify({
#                 "success": False, 
#                 "error": f"Image too large. Max: {MAX_UPLOAD_MB}MB"
#             }), 400

#         # ✅ PREPROCESS IMAGE
#         input_data = preprocess_image(input_data)
#         logger.info(f"After compression: {len(input_data)} bytes")

#         # ✅ Background removal
#         output_data = remove(input_data, session=session)

#         # ✅ Optimize output PNG
#         out_img = Image.open(io.BytesIO(output_data))
#         out_buf = io.BytesIO()
#         out_img.save(out_buf, format="PNG", optimize=True)
#         output_data = out_buf.getvalue()

#         result_b64 = base64.b64encode(output_data).decode("utf-8")

#         return jsonify({
#             "success": True,
#             "message": "Background removed successfully",
#             "processed_image": result_b64,
#             "format": "png",
#             "size_bytes": len(output_data),
#             "data_uri": f"data:image/png;base64,{result_b64}"
#         })

#     except Exception as e:
#         logger.error(f"Error: {e}", exc_info=True)
#         return jsonify({
#             "success": False, 
#             "error": str(e),
#             "tip": "Ensure image is valid (JPG, PNG, etc.)"
#         }), 500


# @app.route('/health')
# def health():
#     return jsonify({
#         "status": "healthy", 
#         "service": "bg-remover",
#         "docker": True,
#         "model_loaded": session is not None
#     })


# # ✅ For local development only (Docker uses gunicorn)
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port, debug=False)


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
