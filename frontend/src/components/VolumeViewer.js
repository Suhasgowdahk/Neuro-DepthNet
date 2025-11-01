import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';

const VolumeViewer = ({ volumeData, dimensions }) => {
    const [loading, setLoading] = useState(true);

    return (
        <div className="volume-viewer" style={{ height: '500px', width: '100%' }}>
            <Canvas shadows>
                <PerspectiveCamera makeDefault position={[0, 0, 5]} />
                <ambientLight intensity={0.5} />
                <directionalLight 
                    position={[10, 10, 5]} 
                    intensity={1} 
                    castShadow 
                />
                <OrbitControls enableDamping dampingFactor={0.05} />
                <VolumeRenderer 
                    volumeData={volumeData} 
                    dimensions={dimensions}
                    onLoad={() => setLoading(false)} 
                />
            </Canvas>
            {loading && (
                <div className="loading-overlay">
                    <span>Loading 3D View...</span>
                </div>
            )}
        </div>
    );
};

function VolumeRenderer({ volumeData, dimensions, onLoad }) {
    const { scene } = useThree();
    const meshRef = useRef();

    useEffect(() => {
        if (!volumeData || !dimensions) return;

        // Create 3D texture from volume data
        const createVolumeTexture = () => {
            const { width, height, depth } = dimensions;
            const size = width * height * depth;
            const data = new Uint8Array(size);

            // Convert base64 volume data to array buffer
            const binaryString = atob(volumeData);
            for (let i = 0; i < binaryString.length; i++) {
                data[i] = binaryString.charCodeAt(i);
            }

            return new THREE.Data3DTexture(
                data,
                width,
                height,
                depth
            );
        };

        // Create volume material using ray marching technique
        const createVolumeMaterial = (volumeTexture) => {
            return new THREE.ShaderMaterial({
                uniforms: {
                    u_volume: { value: volumeTexture },
                    u_threshold: { value: 0.3 },
                    u_opacity: { value: 0.8 }
                },
                vertexShader: `
                    varying vec3 v_position;
                    void main() {
                        v_position = position;
                        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                    }
                `,
                fragmentShader: `
                    uniform sampler3D u_volume;
                    uniform float u_threshold;
                    uniform float u_opacity;
                    varying vec3 v_position;

                    void main() {
                        vec3 pos = v_position * 0.5 + 0.5;
                        float value = texture(u_volume, pos).r;
                        
                        if (value < u_threshold) {
                            discard;
                        }
                        
                        gl_FragColor = vec4(value, value, value, u_opacity);
                    }
                `,
                transparent: true,
                side: THREE.DoubleSide
            });
        };

        try {
            const volumeTexture = createVolumeTexture();
            volumeTexture.needsUpdate = true;

            const material = createVolumeMaterial(volumeTexture);
            const geometry = new THREE.BoxGeometry(1, 1, 1);
            const mesh = new THREE.Mesh(geometry, material);
            
            meshRef.current = mesh;
            scene.add(mesh);
            onLoad();

            return () => {
                scene.remove(mesh);
                geometry.dispose();
                material.dispose();
                volumeTexture.dispose();
            };
        } catch (error) {
            console.error('Error creating 3D volume:', error);
        }
    }, [volumeData, dimensions, scene, onLoad]);

    return null;
}

export default VolumeViewer;