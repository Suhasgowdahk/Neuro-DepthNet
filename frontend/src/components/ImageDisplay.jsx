// src/components/ImageDisplay.jsx
import React from 'react';
import { Card, Col, Row } from 'react-bootstrap';

const ImageDisplay = ({ originalImage, enhancedImage, edgeImage }) => {
  const renderImage = (imageData, title) => {
    if (!imageData) return null;
    
    // Convert array data to base64 image
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const imageWidth = imageData[0].length;
    const imageHeight = imageData.length;
    
    canvas.width = imageWidth;
    canvas.height = imageHeight;
    
    const imgData = ctx.createImageData(imageWidth, imageHeight);
    const data = imgData.data;
    
    for (let i = 0; i < imageHeight; i++) {
      for (let j = 0; j < imageWidth; j++) {
        const idx = (i * imageWidth + j) * 4;
        const pixel = imageData[i][j];
        data[idx] = pixel;     // R
        data[idx + 1] = pixel; // G
        data[idx + 2] = pixel; // B
        data[idx + 3] = 255;   // A
      }
    }
    
    ctx.putImageData(imgData, 0, 0);
    return canvas.toDataURL();
  };

  return (
    <Row className="mb-4">
      <Col md={4}>
        <Card>
          <Card.Header>Original</Card.Header>
          <Card.Body className="text-center">
            <img 
              src={renderImage(originalImage, 'Original')} 
              alt="Original" 
              className="img-fluid"
            />
          </Card.Body>
        </Card>
      </Col>
      <Col md={4}>
        <Card>
          <Card.Header>Enhanced</Card.Header>
          <Card.Body className="text-center">
            <img 
              src={renderImage(enhancedImage, 'Enhanced')} 
              alt="Enhanced" 
              className="img-fluid"
            />
          </Card.Body>
        </Card>
      </Col>
      <Col md={4}>
        <Card>
          <Card.Header>Edge Detection</Card.Header>
          <Card.Body className="text-center">
            <img 
              src={renderImage(edgeImage, 'Edge Detection')} 
              alt="Edge Detection" 
              className="img-fluid"
            />
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
};

export default ImageDisplay;