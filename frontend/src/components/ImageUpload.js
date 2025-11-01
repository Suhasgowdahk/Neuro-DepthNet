import React, { useState, useEffect } from 'react';
import { Card, Row, Col } from 'react-bootstrap';
import Volume3DViewer from './Volume3DViewer';
import ClassificationVisual from './ClassificationVisual';
import ImageProcessor from './ImageProcessor';
import Loading from './Loading';
import './ImageUpload.css';

const ImageUpload = () => {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [previewUrls, setPreviewUrls] = useState([]);
    const [uploadStatus, setUploadStatus] = useState(null);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [view3D, setView3D] = useState(false);
    const [processingStage, setProcessingStage] = useState('');

    const handleFileSelect = (event) => {
        if (!event.target.files || event.target.files.length === 0) {
            return;
        }

        const files = Array.from(event.target.files);
        files.sort((a, b) => a.name.localeCompare(b.name));
        setSelectedFiles(files);

        const urls = files.map(file => URL.createObjectURL(file));
        setPreviewUrls(urls);
    };

    const handleBasicAnalysis = async () => {
        if (!selectedFiles.length) return;

        setLoading(true);
        setError(null);
        setView3D(false);

        const formData = new FormData();
        formData.append('file', selectedFiles[0]);

        try {
            const response = await fetch('http://localhost:5000/api/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Processing failed');

            setResults({
                ...data,
                tumorType: data.tumor_type,
                metrics: {
                    ...data.metrics,
                    depth_mm:
                        typeof data.metrics?.depth_mm === 'number' && !isNaN(data.metrics.depth_mm)
                            ? data.metrics.depth_mm
                            : -1
                }
            });
        } catch (err) {
            console.error('Analysis error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handle3DReconstruction = async () => {
        if (selectedFiles.length < 1) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        selectedFiles.forEach(file => formData.append('slices', file));

        try {
            const response = await fetch('http://localhost:5000/api/reconstruct', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Reconstruction failed');

            setResults(prev => ({
                ...prev,
                reconstruction: data,
                metrics: data.metrics || prev.metrics // update metrics if present in reconstruction response
            }));
            setView3D(true);
        } catch (err) {
            console.error('3D reconstruction error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleAnalyze = async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await fetch('/api/analyze');
            const data = await response.json();

            if (data.success) {
                setResults(data);
            } else {
                setError(data.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            setError('Failed to analyze image');
        } finally {
            setLoading(false);
        }
    };

    const handleUpload = async () => {
        if (!selectedFiles.length) {
            setUploadStatus('Please select files first');
            return;
        }

        try {
            const formData = new FormData();
            selectedFiles.forEach((file, index) => {
                formData.append(`file${index}`, file);
            });

            const response = await fetch('http://localhost:5000/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const result = await response.json();
            setUploadStatus('Upload successful');

            previewUrls.forEach(url => URL.revokeObjectURL(url));
            setPreviewUrls([]);
            setSelectedFiles([]);

            return result;

        } catch (error) {
            console.error('Upload error:', error);
            setUploadStatus(`Upload failed: ${error.message}`);
        }
    };

    useEffect(() => {
        return () => {
            previewUrls.forEach(url => URL.revokeObjectURL(url));
        };
    }, [previewUrls]);

    const renderResults = () => {
        if (!results) return null;

        return (
            <div className="results-container">
                <div className="classification-section">
                    <h3>Tumor Analysis</h3>
                    <div className="tumor-info">
                        <div className="info-item">
                            <label>Tumor Type:</label>
                            <span className="tumor-type">{results.tumor_type || 'Unknown'}</span>
                        </div>
                        <div className="info-item">
                            <label>Confidence:</label>
                            <span className="confidence">
                                {((results.confidence || 0) * 100).toFixed(1)}%
                            </span>
                        </div>
                    </div>
                </div>

                <ImageProcessor 
                    originalImage={results.slices?.[0]?.original}
                    enhancedImages={results.slices?.[0]?.enhanced}
                />

                {results.analysis?.class_probabilities && (
                    <ClassificationVisual 
                        probabilities={results.analysis.class_probabilities} 
                    />
                )}

                <div className="metrics-section">
                    <h3>Measurements</h3>
                    <div className="metrics-grid">
                        <div className="metric-item">
                            <label>Area:</label>
                            <span>{results?.analysis?.measurements?.area_pixels.toFixed(2)} px²</span>
                        </div>
                        <div className="metric-item">
                            <label>Perimeter:</label>
                            <span>{results?.analysis?.measurements?.perimeter_pixels.toFixed(2)} px</span>
                        </div>
                        <div className="metric-item">
                            <label>Circularity:</label>
                            <span>{results?.analysis?.measurements?.circularity.toFixed(3)}</span>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="upload-container">
            <div className="upload-section">
                <h3>Brain Tumor Analysis</h3>
                <input
                    type="file"
                    onChange={handleFileSelect}
                    multiple
                    accept="image/*"
                    className="file-input"
                />

                <div className="preview-container">
                    {previewUrls.map((url, index) => (
                        <img 
                            key={`preview-${index}`}
                            src={url}
                            alt={`Preview ${index + 1}`}
                            className="preview-image"
                        />
                    ))}
                </div>

                <div className="button-group">
                    <button
                        onClick={handleBasicAnalysis}
                        disabled={!selectedFiles.length || loading}
                        className="analysis-button"
                    >
                        Basic Analysis
                    </button>
                    <button
                        onClick={handle3DReconstruction}
                        disabled={!selectedFiles.length || loading}
                        className="reconstruction-button"
                    >
                        3D Reconstruction
                    </button>
                    {view3D && results?.metrics?.depth_mm !== undefined && (
                        <span className="depth-label">
                            Depth value: {Math.max(0, Number(results.metrics.depth_mm)).toFixed(2)} mm
                        </span>
                    )}
                </div>
            </div>

            {loading && <Loading message={processingStage} />}
            {error && <div className="error-message">{error}</div>}
            {uploadStatus && (
                <div className={`status-message ${uploadStatus.includes('failed') ? 'error' : 'success'}`}>
                    {uploadStatus}
                </div>
            )}

            {results && !view3D && (
                <div className="basic-analysis">
                    <Row>
                        <Col md={6}>
                            <Card>
                                <Card.Header>Original Image</Card.Header>
                                <Card.Body>
                                    <img
                                        src={`data:image/png;base64,${results.slices[0].original}`}
                                        alt="Original"
                                        className="result-image"
                                    />
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col md={6}>
                            <Card>
                                <Card.Header>Enhanced Image</Card.Header>
                                <Card.Body>
                                    <img
                                        src={`data:image/png;base64,${results.slices[0].enhanced.clahe}`}
                                        alt="Enhanced"
                                        className="result-image"
                                    />
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                </div>
            )}

            {results?.reconstruction && view3D && (
                <div className="reconstruction-view">
                    <Volume3DViewer 
                        meshData={results.reconstruction.mesh}
                        metrics={results.metrics || results.reconstruction.metrics}
                        tumorType={results.tumor_type || results.tumorType} 
                    />
                    {view3D && results?.metrics?.depth_mm !== undefined && (
                        <span className="depth-label">
                            Depth value: {Math.max(0, Number(results.metrics.depth_mm)).toFixed(2)} mm
                        </span>
                    )}
                </div>
            )}

            {renderResults()}
        </div>
    );
};

export default ImageUpload;
