// src/components/UploadForm.jsx
import React, { useState } from 'react';
import { Form, Button, Spinner } from 'react-bootstrap';

const UploadForm = ({ onUpload }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('image', file);

    try {
      await onUpload(formData);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form onSubmit={handleSubmit} className="mb-4">
      <Form.Group className="mb-3">
        <Form.Label>Upload MRI Scan</Form.Label>
        <Form.Control 
          type="file" 
          onChange={(e) => setFile(e.target.files[0])}
          accept="image/*"
        />
      </Form.Group>
      <Button type="submit" disabled={!file || loading}>
        {loading ? (
          <>
            <Spinner size="sm" className="me-2" />
            Processing...
          </>
        ) : (
          'Analyze Image'
        )}
      </Button>
    </Form>
  );
};

export default UploadForm;