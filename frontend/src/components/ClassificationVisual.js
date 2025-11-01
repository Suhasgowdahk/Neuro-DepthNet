import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import './ClassificationVisual.css';

const ClassificationVisual = ({ probabilities }) => {
    if (!probabilities) return null;

    const data = Object.entries(probabilities).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        probability: (value * 100).toFixed(1)
    }));

    return (
        <div className="classification-visual">
            <h4>Classification Probabilities</h4>
            <ResponsiveContainer width="100%" height={200}>
                <BarChart data={data}>
                    <XAxis dataKey="name" />
                    <YAxis label={{ value: 'Probability (%)', angle: -90 }} />
                    <Tooltip 
                        formatter={(value) => [`${value}%`, 'Probability']}
                    />
                    <Bar dataKey="probability" fill="#4CAF50" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default ClassificationVisual;