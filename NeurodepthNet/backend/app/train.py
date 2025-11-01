# app/train.py
import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical

class ModelTrainer:
    def __init__(self, data_dir=None):
        if data_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self.data_dir = os.path.join(project_root, 'data')
        else:
            self.data_dir = data_dir

        self.image_size = (224, 224)
        self.model = None
        self.classes = ['glioma', 'meningioma', 'notumor', 'pituitary']
        self.num_classes = len(self.classes)

    def load_data(self, subset='training'):
        images = []
        labels = []

        subset_dir = os.path.join(self.data_dir, subset)
        if not os.path.exists(subset_dir):
            raise FileNotFoundError(f"Subset directory not found: {subset_dir}")

        print(f"Loading {subset} data from {subset_dir}...")

        for class_idx, class_name in enumerate(self.classes):
            class_dir = os.path.join(subset_dir, class_name)
            if not os.path.exists(class_dir):
                raise FileNotFoundError(f"Class directory not found: {class_dir}")

            print(f"Loading images for class: {class_name}")
            for img_name in os.listdir(class_dir):
                if img_name.lower().endswith(('.jpg', '.png', '.jpeg')):
                    img_path = os.path.join(class_dir, img_name)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        img = cv2.resize(img, self.image_size)
                        images.append(img)
                        labels.append(class_idx)
                    else:
                        print(f"Warning: Failed to load image: {img_path}")

        if not images or not labels:
            raise ValueError(f"No images found in {subset_dir}")

        return np.array(images), np.array(labels)

    def create_model(self):
        self.model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(*self.image_size, 1)),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(128, activation='relu'),
            Dropout(0.5),
            Dense(64, activation='relu'),
            Dropout(0.3),
            Dense(self.num_classes, activation='softmax')
        ])

        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

    def train(self):
        try:
            # Load training and testing data
            print("Loading training data...")
            X_train, y_train = self.load_data('training')
            print("Loading testing data...")
            X_test, y_test = self.load_data('testing')
            
            print(f"Training samples: {len(X_train)}")
            print(f"Testing samples: {len(X_test)}")

            # Reshape and normalize images
            X_train = X_train.reshape(-1, *self.image_size, 1) / 255.0
            X_test = X_test.reshape(-1, *self.image_size, 1) / 255.0

            # Convert labels to categorical
            y_train = to_categorical(y_train, self.num_classes)
            y_test = to_categorical(y_test, self.num_classes)

            # Create and train model
            print("Creating the model...")
            self.create_model()
            
            print("Starting training...")
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_test, y_test),
                epochs=250,  # Increased from 1 to 10
                batch_size=32,
                verbose=1  # Add verbose output
            )

            # Save model - using absolute path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            models_dir = os.path.join(project_root, 'models')
            os.makedirs(models_dir, exist_ok=True)
            
            model_path = os.path.join(models_dir, 'tumor_model.h5')
            print(f"Saving model to: {model_path}")
            self.model.save(model_path)
            print(f"Model saved successfully!")

            # Evaluate model
            print("\nEvaluating model...")
            test_loss, test_accuracy = self.model.evaluate(X_test, y_test)
            print(f"Test accuracy: {test_accuracy:.4f}")

            return history

        except Exception as e:
            print(f"Error during training: {str(e)}")
            raise e

if __name__ == "__main__":
    print("Starting tumor classification model training...")
    trainer = ModelTrainer()
    try:
        history = trainer.train()
        print("Training completed successfully!")
    except Exception as e:
        print(f"Training failed: {str(e)}")