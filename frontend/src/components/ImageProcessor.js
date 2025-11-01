import React from 'react';
import { Card, Row, Col } from 'react-bootstrap';
import './ImageProcessor.css';

const ImageProcessor = ({ originalImage, enhancedImages }) => {
    if (!originalImage || !enhancedImages) return null;

    return (
        <div className="image-processor">
            <Row>
                <Col md={6}>
                    <Card>
                        <Card.Header>Original Image</Card.Header>
                        <Card.Body>
                            <img
                                src={`data:image/png;base64,${originalImage}`}
                                alt="Original"
                                className="processed-image"
                            />
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={6}>
                    <Card>
                        <Card.Header>Enhanced Image (CLAHE)</Card.Header>
                        <Card.Body>
                            <img
                                src={`data:image/png;base64,${enhancedImages.clahe}`}
                                alt="Enhanced"
                                className="processed-image"
                            />
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
            <Row className="mt-3">
                <Col md={6}>
                    <Card>
                        <Card.Header>Edge Detection</Card.Header>
                        <Card.Body>
                            <img
                                src={`data:image/png;base64,${enhancedImages.edges}`}
                                alt="Edges"
                                className="processed-image"
                            />
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={6}>
                    <Card>
                        <Card.Header>Filtered Image</Card.Header>
                        <Card.Body>
                            <img
                                src={`data:image/png;base64,${enhancedImages.filtered}`}
                                alt="Filtered"
                                className="processed-image"
                            />
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default ImageProcessor;