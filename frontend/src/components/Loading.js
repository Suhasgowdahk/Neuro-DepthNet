import React from 'react';
import './Loading.css';

const Loading = ({ message }) => {
    return (
        <div className="loading-container">
            <div className="spinner"></div>
            <p className="loading-text">{message || 'Processing...'}</p>
        </div>
    );
};

export default Loading;