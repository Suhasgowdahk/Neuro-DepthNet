import cv2
from tumor_classification import TumorClassifier

def test_classifier():
    # Initialize the classifier with the trained model
    classifier = TumorClassifier(model_path='../models/tumor_model.h5')
    
    # Load a test image (replace with path to your test image)
    test_image_path = '../data/testing/glioma/glioma_test1.jpg'  # adjust path as needed
    test_image = cv2.imread(test_image_path, cv2.IMREAD_GRAYSCALE)
    
    if test_image is None:
        print(f"Failed to load test image from {test_image_path}")
        return
    
    # Get prediction
    result = classifier.classify(test_image)
    
    # Print results
    print("\nClassification Results:")
    print(f"Predicted class: {result['class']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print("\nClass probabilities:")
    for class_name, probability in result['probabilities'].items():
        print(f"{class_name}: {probability:.2%}")

if __name__ == "__main__":
    test_classifier()