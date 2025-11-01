// src/components/Results.jsx
import React from 'react';
import { Alert } from 'react-bootstrap';

const Results = ({ classification }) => {
  if (!classification) return null;

  return (
    <Alert variant={classification.class === 'Tumor' ? 'warning' : 'success'}>
      <h4>Analysis Results</h4>
      <p>Classification: {classification.class}</p>
      <p>Confidence: {(classification.confidence * 100).toFixed(2)}%</p>
    </Alert>
  );
};

export default Results;