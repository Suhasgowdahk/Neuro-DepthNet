import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
from app.data_loader import DataLoader
from app.image_processing import ImageProcessor
from app.tumor_classification import TumorClassifier

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.data_loader = DataLoader()
        self.image_processor = ImageProcessor()
        self.tumor_classifier = TumorClassifier()

    def test_data_loading(self):
        """Test if data can be loaded correctly"""
        images, labels = self.data_loader.load_dataset()
        self.assertIsNotNone(images)
        self.assertIsNotNone(labels)
        self.assertEqual(len(images), len(labels))
        
    def test_image_processing(self):
        """Test image enhancement"""
        # Get first image from dataset
        images, _ = self.data_loader.load_dataset()
        if len(images) > 0:
            image = images[0]
            results = self.image_processor.enhance_image(image)
            
            self.assertIn('enhanced', results)
            self.assertIn('filtered', results)
            self.assertIn('edges', results)
            
            # Check shapes match
            self.assertEqual(image.shape, results['enhanced'].shape)
            
    def test_classification(self):
        """Test tumor classification"""
        images, _ = self.data_loader.load_dataset()
        if len(images) > 0:
            image = images[0]
            result = self.tumor_classifier.classify(image)
            
            self.assertIn('class', result)
            self.assertIn('confidence', result)
            self.assertIn(result['class'], ['Tumor', 'No Tumor'])
            self.assertTrue(0 <= result['confidence'] <= 1)

if __name__ == '__main__':
    unittest.main()