# app_optimized.py - 512MB-এ চলবে
import os
import gc
import logging
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import base64

# Memory optimization
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LAZY LOADING - Model loads only when needed
_MODEL = None
_SESSION = None

def get_session():
    """Lazy load model to save memory"""
    global _SESSION, _MODEL
    if _SESSION is None:
        logger.info("⏳ Loading rembg model (first time only)...")
        
        # Import here to delay loading
        from rembg import new_session
        
        # Use smallest model
        _SESSION = new_session("u2netp")
        
        # Force garbage collection
        gc.collect()
        
        logger.info("✅ Model loaded successfully")
    
    return _SESSION

@app.route('/health', methods=['GET'])
def health():
    """Lightweight health check"""
    return jsonify({
        "status": "healthy",
        "memory": "optimized",
        "service": "bg-remover-lite"
    })

@app.route('/remove-background', methods=['POST'])
def remove_background():
    """Optimized background removal"""
    start_time = time.time()
    
    try:
        # Get image
        if 'image' not in request.files:
            return jsonify({"error": "No image"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read image
        image_data = file.read()
        
        # Check size (max 2MB for free tier)
        if len(image_data) > 2 * 1024 * 1024:
            return jsonify({"error": "Image too large (max 2MB)"}), 400
        
        # Resize image before processing
        from PIL import Image
        import io as image_io
        
        img = Image.open(image_io.BytesIO(image_data))
        
        # Resize to save memory
        max_size = (512, 512)
        img.thumbnail(max_size)
        
        # Convert to RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Save compressed image
        buffer = image_io.BytesIO()
        img.save(buffer, format='JPEG', quality=70, optimize=True)
        compressed_data = buffer.getvalue()
        
        # Load model (lazy)
        session = get_session()
        
        # Process with rembg
        from rembg import remove
        
        output = remove(compressed_data, session=session)
        
        # Convert to base64
        result_b64 = base64.b64encode(output).decode('utf-8')
        
        # Force cleanup
        del img, buffer, compressed_data, output
        gc.collect()
        
        processing_time = time.time() - start_time
        
        return jsonify({
            "success": True,
            "processed_image": result_b64,
            "processing_time": f"{processing_time:.2f}s",
            "memory_optimized": True
        })
        
    except MemoryError:
        logger.error("🔄 Out of memory! Forcing cleanup...")
        gc.collect()
        return jsonify({
            "error": "Server out of memory. Try smaller image.",
            "code": "MEMORY_LIMIT"
        }), 500
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    # Use lightweight server
    from waitress import serve
    logger.info(f"🚀 Starting optimized server on port {port}")
    serve(app, host='0.0.0.0', port=port, threads=1)