import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    def enhance_image(self, image):
        """Apply various enhancement techniques"""
        # CLAHE enhancement
        clahe_img = self.clahe.apply(image)

        # Bilateral filtering
        filtered = cv2.bilateralFilter(clahe_img, 9, 75, 75)

        # Edge detection
        edges = cv2.Canny(filtered, 100, 200)

        return {
            'clahe': clahe_img,
            'filtered': filtered,
            'edges': edges
        }