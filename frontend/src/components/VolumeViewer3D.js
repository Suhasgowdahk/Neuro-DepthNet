import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const VolumeViewer3D = ({ meshData, metrics }) => {
    const mountRef = useRef(null);

    useEffect(() => {
        if (!meshData) return;

        // Set up scene
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
        mountRef.current.appendChild(renderer.domElement);

        // Add mesh to scene
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(meshData.vertices, 3));
        geometry.setAttribute('normal', new THREE.Float32BufferAttribute(meshData.normals, 3));
        geometry.setIndex(meshData.indices);

        const material = new THREE.MeshPhongMaterial({
            color: 0x00ff00,
            opacity: 0.8,
            transparent: true,
            side: THREE.DoubleSide
        });

        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(0, 1, 0);
        scene.add(directionalLight);

        // Set up controls
        const controls = new OrbitControls(camera, renderer.domElement);
        camera.position.z = 5;

        // Animation loop
        const animate = () => {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        };
        animate();

        // Cleanup
        return () => {
            mountRef.current?.removeChild(renderer.domElement);
            geometry.dispose();
            material.dispose();
        };
    }, [meshData]);

    return (
        <div className="volume-viewer-3d">
            <div ref={mountRef} className="render-container"></div>
            {metrics && (
                <div className="metrics-overlay">
                    <h4>Tumor Metrics</h4>
                    <p>Volume: {metrics.volume_mm3.toFixed(2)} mm³</p>
                    <p>Surface Area: {metrics.surface_area_mm2.toFixed(2)} mm²</p>
                    <p>Depth: {metrics.depth_mm.toFixed(2)} mm</p>
                    <p>Number of Slices: {metrics.num_slices}</p>
                </div>
            )}
        </div>
    );
};

export default VolumeViewer3D;