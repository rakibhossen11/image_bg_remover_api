@app.route('/remove-background', methods=['POST', 'OPTIONS'])
def remove_background():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # [Same code for getting input_data...]
        # ...
        
        # ✅ Convert to PIL Image with better error handling
        try:
            img = Image.open(io.BytesIO(input_data))
            
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            elif img.mode != 'RGB':
                img = img.convert('RGB')
                
        except Exception as e:
            logger.error(f"Image open error: {e}")
            return jsonify({
                "success": False, 
                "error": f"Cannot process image: {str(e)}"
            }), 400

        # ✅ Resize if too large
        img.thumbnail(MAX_IMAGE_SIZE)
        
        # ✅ Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        
        logger.info(f"Processed image size: {len(img_bytes)} bytes")

        # ✅ TRY DIFFERENT APPROACHES IF FIRST FAILS
        try:
            # Method 1: Direct bytes removal
            output = remove(img_bytes, session=session)
        except Exception as e1:
            logger.warning(f"Method 1 failed: {e1}, trying Method 2...")
            try:
                # Method 2: PIL Image removal
                output = remove(img, session=session)
            except Exception as e2:
                logger.warning(f"Method 2 failed: {e2}, trying Method 3...")
                try:
                    # Method 3: Convert to RGBA and then remove
                    img_rgba = img.convert('RGBA')
                    output = remove(img_rgba, session=session)
                except Exception as e3:
                    logger.error(f"All methods failed: {e3}")
                    return jsonify({
                        "success": False, 
                        "error": "Failed to remove background. Try a different image format.",
                        "details": str(e3)
                    }), 500

        # ✅ Convert output to base64
        if hasattr(output, 'tobytes'):
            # If output is a PIL Image
            output_buffer = io.BytesIO()
            output.save(output_buffer, format="PNG")
            output_data = output_buffer.getvalue()
        else:
            # If output is bytes
            output_data = output

        result_b64 = base64.b64encode(output_data).decode("utf-8")

        return jsonify({
            "success": True,
            "message": "Background removed successfully",
            "processed_image": result_b64,
            "format": "png",
            "size_bytes": len(output_data),
            "data_uri": f"data:image/png;base64,{result_b64}"
        })

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({
            "success": False, 
            "error": str(e),
            "tip": "Ensure image is valid (JPG, PNG, etc.)"
        }), 500


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
