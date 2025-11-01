import React from 'react';
import './EnhancementControls.css';

const EnhancementControls = ({ onParamChange, params }) => {
    return (
        <div className="enhancement-controls">
            <div className="control-group">
                <h4>CLAHE Parameters</h4>
                <label>
                    Clip Limit:
                    <input
                        type="range"
                        min="1"
                        max="5"
                        step="0.1"
                        value={params.claheClipLimit}
                        onChange={(e) => onParamChange('claheClipLimit', e.target.value)}
                    />
                    <span>{params.claheClipLimit}</span>
                </label>
            </div>

            <div className="control-group">
                <h4>Bilateral Filter</h4>
                <label>
                    Sigma:
                    <input
                        type="range"
                        min="1"
                        max="100"
                        value={params.bilateralSigma}
                        onChange={(e) => onParamChange('bilateralSigma', e.target.value)}
                    />
                    <span>{params.bilateralSigma}</span>
                </label>
            </div>

            <div className="control-group">
                <h4>Edge Detection</h4>
                <label>
                    Threshold:
                    <input
                        type="range"
                        min="0"
                        max="255"
                        value={params.edgeThreshold}
                        onChange={(e) => onParamChange('edgeThreshold', e.target.value)}
                    />
                    <span>{params.edgeThreshold}</span>
                </label>
            </div>
        </div>
    );
};

export default EnhancementControls;