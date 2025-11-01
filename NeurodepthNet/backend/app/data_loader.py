# app/data_loader.py
import os
import numpy as np
from sklearn.model_selection import train_test_split
import cv2

class DataLoader:
    def __init__(self, data_dir="../data"):
        self.data_dir = data_dir
        
    def load_dataset(self):
        """Load and preprocess the entire dataset"""
        images = []
        labels = []
        
        # Assume 'data' directory has 'tumor' and 'no_tumor' subdirectories
        for class_idx, class_name in enumerate(['no_tumor', 'tumor']):
            class_dir = os.path.join(self.data_dir, class_name)
            if not os.path.exists(class_dir):
                continue
                
            for filename in os.listdir(class_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(class_dir, filename)
                    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if image is not None:
                        image = cv2.resize(image, (224, 224))
                        images.append(image)
                        labels.append(class_idx)
        
        return np.array(images), np.array(labels)
        
    def get_train_test_split(self, test_size=0.2, random_state=42):
        """Split the dataset into training and testing sets"""
        images, labels = self.load_dataset()
        return train_test_split(
            images, labels, 
            test_size=test_size, 
            random_state=random_state, 
            stratify=labels
        )