import cv2
import numpy as np
from skimage import exposure
import os
import SimpleITK as sitk
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self, data_dir="../data"):
        self.data_dir = data_dir
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.logger = logging.getLogger(__name__)
        
    def load_image(self, file_path):
        """Load and preprocess a single image"""
        image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        return image if image is not None else None

    def enhance_image(self, image):
        """Apply various enhancement techniques to the image"""
        try:
            # Verify input
            if image is None:
                raise ValueError("Input image is None")

            # Apply CLAHE enhancement
            clahe_img = self.clahe.apply(image)
            self.logger.debug("Applied CLAHE enhancement")

            # Apply bilateral filtering for noise reduction
            filtered = cv2.bilateralFilter(clahe_img, 9, 75, 75)
            self.logger.debug("Applied bilateral filtering")

            # Edge detection using Canny
            edges = cv2.Canny(filtered, 100, 200)
            self.logger.debug("Applied edge detection")

            return {
                'clahe': clahe_img,
                'filtered': filtered,
                'edges': edges
            }

        except Exception as e:
            self.logger.error(f"Error in enhance_image: {str(e)}")
            raise

    def process_directory(self, subdir='training'):
        """Process all images in a directory"""
        dir_path = os.path.join(self.data_dir, subdir)
        results = []
        
        for filename in os.listdir(dir_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(dir_path, filename)
                image = self.load_image(file_path)
                if image is not None:
                    enhanced_results = self.enhance_image(image)
                    results.append({
                        'filename': filename,
                        'original': image,
                        **enhanced_results
                    })
        
        return results

    def reconstruct_3d(self, image_slices, slice_thickness=1.0):
        """Reconstruct 3D volume from multiple slices"""
        try:
            # Convert slices to SimpleITK image
            sitk_slices = [sitk.GetImageFromArray(slice) for slice in image_slices]
            
            # Set physical spacing (slice thickness)
            for img in sitk_slices:
                img.SetSpacing([1.0, 1.0, slice_thickness])

            # Concatenate slices into 3D volume
            volume = sitk.JoinSeries(sitk_slices)
            
            # Apply 3D processing
            volume = sitk.DiscreteGaussian(volume)
            
            # Calculate tumor depth
            depth_mm = len(image_slices) * slice_thickness
            
            return {
                'volume': sitk.GetArrayFromImage(volume),
                'depth_mm': depth_mm
            }
        except Exception as e:
            raise Exception(f"3D reconstruction failed: {str(e)}")

class TumorAnalyzer:
    def analyze_slices(self, slices):
        # Convert to SimpleITK image
        sitk_images = [sitk.GetImageFromArray(slice) for slice in slices]
        volume = sitk.JoinSeries(sitk_images)
        
        # Set physical spacing (assuming 1mm slice thickness)
        volume.SetSpacing([1.0, 1.0, 1.0])
        
        # Segment tumor
        otsu = sitk.OtsuThresholdImageFilter()
        mask = otsu.Execute(volume)
        
        # Calculate tumor properties
        stats = sitk.LabelShapeStatisticsImageFilter()
        stats.Execute(mask)
        
        # Get 3D measurements
        depth = stats.GetBoundingBox(1)[5] * volume.GetSpacing()[2]
        volume_mm3 = stats.GetPhysicalSize(1)
        
        return {
            'depth_mm': depth,
            'volume_mm3': volume_mm3,
            'center': stats.GetCentroid(1)
        }