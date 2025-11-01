# app/tumor_classification.py
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
import cv2
import logging

class TumorClassifier:
    def __init__(self, model_path='../models/tumor_model.h5'):
        self.model = tf.keras.models.load_model(model_path)
        self.image_size = (224, 224)
        self.classes = ['glioma', 'meningioma', 'notumor', 'pituitary']
        self.logger = logging.getLogger(__name__)

    def preprocess_image(self, image):
        # Resize and normalize
        image = cv2.resize(image, self.image_size)
        image = image.reshape(-1, *self.image_size, 1) / 255.0
        return image

    def classify(self, image):
        preprocessed = self.preprocess_image(image)
        prediction = self.model.predict(preprocessed)
        class_idx = np.argmax(prediction[0])
        confidence = float(prediction[0][class_idx])
        
        return {
            'class': self.classes[class_idx],
            'confidence': confidence,
            'probabilities': {
                class_name: float(prob) 
                for class_name, prob in zip(self.classes, prediction[0])
            }
        }

    def get_confidence(self, image):
        """Get confidence score for tumor classification
        
        Args:
            image: numpy array of grayscale image
            
        Returns:
            float: confidence score between 0 and 1
        """
        try:
            # Preprocess image
            preprocessed = self.preprocess_image(image)
            
            # Get prediction
            prediction = self.model.predict(preprocessed)
            
            # Return highest confidence score
            return float(np.max(prediction))
            
        except Exception as e:
            self.logger.error(f"Error getting confidence: {str(e)}")
            return 0.0