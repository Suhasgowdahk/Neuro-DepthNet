// src/components/ThreeDViewer.jsx
import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const ThreeDViewer = ({ slices, tumorData }) => {
    const mountRef = useRef(null);

    useEffect(() => {
        if (!slices || !tumorData) return;

        // Three.js setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        
        renderer.setSize(500, 500);
        mountRef.current.appendChild(renderer.domElement);

        // Create volume visualization
        const geometry = new THREE.BoxGeometry(
            1, 
            1, 
            tumorData.depth_mm / 10
        );
        const material = new THREE.MeshPhongMaterial({ color: 0xff0000, opacity: 0.6, transparent: true });
        const tumor = new THREE.Mesh(geometry, material);
        
        scene.add(tumor);
        
        // Add lighting
        const light = new THREE.PointLight(0xffffff, 1, 100);
        light.position.set(10, 10, 10);
        scene.add(light);
        
        camera.position.z = 5;
        
        // Add controls
        const controls = new OrbitControls(camera, renderer.domElement);
        
        const animate = () => {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        };
        
        animate();
        
        return () => {
            mountRef.current.removeChild(renderer.domElement);
        };
    }, [slices, tumorData]);

    return (
        <div ref={mountRef}>
            <div style={{position: 'absolute', padding: '10px', background: 'rgba(0,0,0,0.7)', color: 'white'}}>
                <p>Tumor Depth: {tumorData?.depth_mm.toFixed(2)} mm</p>
                <p>Volume: {tumorData?.volume_mm3.toFixed(2)} mm³</p>
            </div>
        </div>
    );
};

export default ThreeDViewer;