import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import './Volume3DViewer.css';

const Volume3DViewer = ({ meshData, metrics, tumorType }) => {
    const mountRef = useRef(null);

    // Log incoming props
    useEffect(() => {
        console.log('Volume3DViewer Props:', {
            tumorType,
            metrics,
            meshData: !!meshData
        });
    }, [tumorType, metrics, meshData]);

    // Calculate display value
    const getDepthDisplay = () => {
        let val = metrics?.depth_mm;
        if (val === undefined || val === null || isNaN(Number(val))) {
            return "0.00";
        }
        const numVal = Math.max(0, Number(val));
        return numVal.toFixed(2);
    };

    useEffect(() => {
        if (!meshData?.vertices || !mountRef.current) return;

        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000000);

        // Camera setup
        const camera = new THREE.PerspectiveCamera(
            75,
            mountRef.current.clientWidth / mountRef.current.clientHeight,
            0.1,
            1000
        );
        camera.position.z = 5;

        // Renderer setup
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
        mountRef.current.appendChild(renderer.domElement);

        // Create mesh
        const geometry = new THREE.BufferGeometry();
        const vertices = new Float32Array(meshData.vertices.flat());
        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
        
        if (meshData.faces) {
            const indices = new Uint32Array(meshData.faces.flat());
            geometry.setIndex(new THREE.BufferAttribute(indices, 1));
        }
        
        geometry.computeVertexNormals();

        const material = new THREE.MeshPhongMaterial({
            color: 0xff3333, // bright red for spikes
            opacity: 0.95,
            transparent: true,
            side: THREE.DoubleSide,
            shininess: 100,
        });

        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(0, 1, 1);
        scene.add(directionalLight);

        // Controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // Center mesh
        geometry.computeBoundingSphere();
        const { center, radius } = geometry.boundingSphere;
        mesh.position.sub(center);
        camera.position.z = radius * 3;

        // Animation
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
        <div className="volume-viewer">
            <div className="render-container" ref={mountRef} />
            <div className="metrics-overlay">
                <div className="metric-item">
                    <label>Depth:</label>
                    <span style={{ color: tumorType?.toLowerCase() === 'notumor' ? '#ff9800' : '#4CAF50' }}>
                        {getDepthDisplay()} mm
                    </span>
                </div>
            </div>
        </div>
    );
};

export default Volume3DViewer;

