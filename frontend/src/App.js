// src/App.js
import React from 'react';
import './App.css';
import ImageUpload from './components/ImageUpload';

function App() {
  return (
    <div className="App">
      <div className="background-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
        <div className="shape shape-3"></div>
      </div>
      
      <header className="app-header">
        <div className="logo-container">
          <div className="logo-icon">🧠</div>
        </div>
        <h1 className="app-title">NeuroDepthNet: A Deep Learning-Based System for Brain Tumor  Classification and Depth Estimation</h1>
        <p className="app-subtitle">
          Advanced medical imaging analysis tool for detecting and classifying brain tumors 
          using state-of-the-art machine learning techniques
        </p>
        <div className="header-decoration"></div>
      </header>
      
      <main className="content-wrapper">
        <ImageUpload />
      </main>
    </div>
  );
}

export default App;