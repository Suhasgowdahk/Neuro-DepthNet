# app/routes.py
from flask import request, jsonify
from flask_cors import CORS, cross_origin
from .image_processing import ImageProcessor
from .tumor_classification import TumorClassifier
from .tumor_segmentation import TumorSegmentation
from .reconstruction import VolumeReconstructor
from .reconstruction3d import Reconstructor3D
import numpy as np
import cv2
import logging
import os
import base64

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def encode_image(image_array):
    try:
        if image_array is None:
            return None
            
        # Ensure image is in uint8 format
        if image_array.dtype != np.uint8:
            image_array = (image_array * 255).astype(np.uint8)
            
        # Encode to png
        success, encoded_image = cv2.imencode('.png', image_array)
        if not success:
            return None
            
        # Convert to base64
        return base64.b64encode(encoded_image.tobytes()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {str(e)}")
        return None

def setup_routes(app):
    # Enable CORS for all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Get absolute path to model file at startup
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    model_path = os.path.join(project_root, 'models', 'tumor_model.h5')
    
    # Verify model exists at startup
    if not os.path.exists(model_path):
        logger.error(f"Model file not found at {model_path}")
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    logger.info(f"Using model from: {model_path}")
    
    image_processor = ImageProcessor()
    tumor_classifier = TumorClassifier(model_path=model_path)
    tumor_segmentation = TumorSegmentation()
    reconstructor = VolumeReconstructor()
    reconstructor_3d = Reconstructor3D()

    @app.route('/api/process', methods=['POST'])
    @cross_origin()
    def process_image():
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400

            file = request.files['file']
            file_bytes = file.read()
            
            # Decode image
            nparr = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            if img is None:
                return jsonify({"error": "Invalid image format"}), 400

            # Process image
            enhanced = image_processor.enhance_image(img)
            measurements = tumor_segmentation.calculate_measurements(img)
            classification = tumor_classifier.classify(img)

            response = {
                "success": True,
                "tumor_type": classification['class'],
                "confidence": classification['confidence'],
                "slices": [{
                    "original": encode_image(img),
                    "enhanced": {
                        "clahe": encode_image(enhanced['clahe']),
                        "filtered": encode_image(enhanced['filtered']),
                        "edges": encode_image(enhanced['edges']),
                        "segmented": encode_image(tumor_segmentation.get_segmentation_overlay(img))
                    }
                }],
                "analysis": {
                    "measurements": measurements,
                    "class_probabilities": classification['probabilities']
                }
            }

            return jsonify(response)

        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    def encode_image_base64(img):
        """Convert image to base64 string"""
        success, encoded = cv2.imencode('.png', img)
        if not success:
            return None
        return base64.b64encode(encoded.tobytes()).decode('utf-8')

    @app.route('/api/classify', methods=['POST'])
    def classify_image():
        try:
            if 'image' not in request.files:
                logger.error("No image file in request")
                return jsonify({'error': 'No image provided'}), 400
            
            file = request.files['image']
            
            # Read and preprocess the image
            file_bytes = file.read()
            img_array = cv2.imdecode(
                np.frombuffer(file_bytes, np.uint8), 
                cv2.IMREAD_GRAYSCALE
            )
            
            if img_array is None:
                logger.error("Failed to decode image")
                return jsonify({"error": "Invalid image format"}), 400
            
            # Use existing classifier instance
            result = tumor_classifier.classify(img_array)
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/train", methods=["POST"])
    def train_model():
        """Train the model using the data directory"""
        # Add training logic here
        return jsonify({"message": "Training started"})

    @app.route('/api/enhance', methods=['POST'])
    def enhance_image():
        try:
            data = request.json
            image_data = base64.b64decode(data['image'])
            params = data['params']
            
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            # Apply CLAHE
            clahe = cv2.createCLAHE(clipLimit=float(params['claheClipLimit']), tileGridSize=(8,8))
            enhanced = clahe.apply(img)
            
            # Apply bilateral filter
            filtered = cv2.bilateralFilter(enhanced, 9, 
                                         float(params['bilateralSigma']), 
                                         float(params['bilateralSigma']))
            
            # Edge detection
            edges = cv2.Canny(filtered, 
                             float(params['edgeThreshold'])/2, 
                             float(params['edgeThreshold']))
            
            return jsonify({
                'clahe': encode_image(enhanced),
                'filtered': encode_image(filtered),
                'edges': encode_image(edges)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/process-volume', methods=['POST'])
    def process_volume():
        try:
            files = request.files.getlist('images')
            if not files:
                return jsonify({"error": "No images provided"}), 400

            # Convert uploaded images to numpy arrays
            slices = []
            for file in files:
                nparr = np.frombuffer(file.read(), np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                slices.append(img)

            # Create 3D volume
            volume = reconstructor.create_volume_from_slices(slices)
            
            # Segment tumor in 3D
            tumor_mask = reconstructor.segment_tumor_3d(volume)
            
            # Calculate 3D metrics
            metrics = reconstructor.calculate_tumor_metrics(tumor_mask)
            
            # Generate 3D mesh
            mesh = reconstructor.generate_3d_mesh(tumor_mask)

            # Convert mesh to a format suitable for web visualization
            # (You'll need to implement this based on your frontend needs)

            return jsonify({
                'metrics': metrics,
                'mesh_data': mesh_data,  # Implement conversion to suitable format
                'num_slices': len(slices),
                'slice_thickness': reconstructor.slice_thickness
            })

        except Exception as e:
            logger.error(f"3D reconstruction error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/reconstruct', methods=['POST'])
    @cross_origin()
    def reconstruct_volume():
        try:
            files = request.files.getlist('slices')
            logger.debug(f"Received {len(files)} files")
            
            slices = []
            for file in files:
                file_bytes = file.read()
                nparr = np.frombuffer(file_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    slices.append(img)
                    
            if not slices:
                return jsonify({"error": "No valid images provided"}), 400

            # Get tumor classification from middle slice
            middle_slice = slices[len(slices)//2]
            classification = tumor_classifier.classify(middle_slice)
            measurements = tumor_segmentation.calculate_measurements(middle_slice)

            detected_type = classification['class'].lower().strip()

            # Create reconstructor and process volume
            reconstructor = VolumeReconstructor()
            volume = reconstructor.create_volume_from_slices(slices)
            tumor_mask = reconstructor.segment_tumor_3d(volume)
            volume_metrics = reconstructor.calculate_tumor_metrics(tumor_mask)
            enhanced_metrics = {
                **volume_metrics,
                **measurements,
                "tumor_type": classification['class'],
                "confidence": classification['confidence'],
                "num_slices": len(slices)
            }
            mesh_data = reconstructor.generate_3d_mesh(tumor_mask)

            # Force depth_mm to 0.0 for notumor
            if detected_type in ['notumor', 'notumor tumor', 'no tumor']:
                logger.info("Detected notumor, setting depth_mm to 0.0 but returning mesh.")
                enhanced_metrics["depth_mm"] = 0.0

            response = {
                "success": True,
                "metrics": enhanced_metrics,
                "mesh": mesh_data,
                "classification": {
                    "tumor_type": classification['class'],
                    "confidence": classification['confidence'],
                    "probabilities": classification['probabilities']
                }
            }
            return jsonify(response)

        except Exception as e:
            logger.error(f"Reconstruction error: {str(e)}", exc_info=True)
            return jsonify({"error": str(e), "success": False}), 500

    return app