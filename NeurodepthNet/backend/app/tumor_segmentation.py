import cv2
import numpy as np
from skimage import measure
from scipy import ndimage
import logging

logger = logging.getLogger(__name__)

class TumorSegmentation:
    def __init__(self):
        self.mask = None
        self.contours = None
        self.logger = logging.getLogger(__name__)
        
    def segment_tumor(self, image):
        """Segment tumor from the brain MRI image"""
        # Convert to float and normalize
        img = image.astype(float) / 255.0
        
        # Apply Otsu's thresholding
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Remove noise using morphological operations
        kernel = np.ones((3,3), np.uint8)
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Find connected components
        labels = measure.label(opening)
        props = measure.regionprops(labels)
        
        # Get the largest connected component (assumed to be tumor)
        if props:
            largest = max(props, key=lambda p: p.area)
            self.mask = (labels == largest.label).astype(np.uint8) * 255
            self.contours, _ = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            return {
                'mask': self.mask,
                'measurements': self.calculate_measurements(),
                'contours': self.contours
            }
        return None
    
    def calculate_measurements(self, image):
        """Calculate tumor measurements from image"""
        try:
            # Threshold image using Otsu's method
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return {
                    'area_pixels': 0,
                    'perimeter_pixels': 0,
                    'circularity': 0
                }
            
            # Get largest contour (assumed to be tumor)
            tumor_contour = max(contours, key=cv2.contourArea)
            
            # Calculate metrics
            area = cv2.contourArea(tumor_contour)
            perimeter = cv2.arcLength(tumor_contour, True)
            
            # Calculate circularity (4π * area / perimeter²)
            circularity = (4 * np.pi * area) / (perimeter * perimeter) if perimeter > 0 else 0
            
            self.logger.info(f"Area: {area}, Perimeter: {perimeter}, Circularity: {circularity}")
            
            return {
                'area_pixels': float(area),
                'perimeter_pixels': float(perimeter),
                'circularity': float(circularity)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating measurements: {str(e)}")
            raise

    def get_segmentation_overlay(self, image):
        """Create a colored overlay showing tumor segmentation on the original image
        
        Args:
            image: numpy array of grayscale image
            
        Returns:
            numpy array: RGB image with colored tumor overlay
        """
        try:
            # Threshold image using Otsu's method
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return image
            
            # Get largest contour (assumed to be tumor)
            tumor_contour = max(contours, key=cv2.contourArea)
            
            # Create RGB image from grayscale
            rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            # Create overlay mask
            overlay = np.zeros_like(rgb_image)
            cv2.drawContours(overlay, [tumor_contour], -1, (0, 255, 0), 2)  # Green contour
            cv2.fillPoly(overlay, [tumor_contour], (0, 255, 0, 128))  # Semi-transparent fill
            
            # Blend original image with overlay
            alpha = 0.3  # Transparency factor
            overlay_image = cv2.addWeighted(rgb_image, 1, overlay, alpha, 0)
            
            self.logger.debug("Generated segmentation overlay")
            return overlay_image
            
        except Exception as e:
            self.logger.error(f"Error creating segmentation overlay: {str(e)}")
            return image