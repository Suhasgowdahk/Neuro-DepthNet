import numpy as np
from scipy import ndimage
from scipy.spatial import ConvexHull
from skimage import measure

class MeshEnhancer:
    @staticmethod
    def create_dramatic_spikes(vertices, faces, base_intensity=5.0):
        """Create extreme spikes and variations in the mesh"""
        # Calculate vertex normals with high intensity
        vertex_normals = np.zeros_like(vertices)
        weights = np.zeros(len(vertices))
        
        for face in faces:
            v0, v1, v2 = vertices[face]
            normal = np.cross(v1 - v0, v2 - v0)
            length = np.linalg.norm(normal)
            if length > 0:
                normal = normal / length
                # Add random weight to each face
                weight = np.random.uniform(1.5, 3.0)
                vertex_normals[face] += normal * weight
                weights[face] += weight

        # Normalize and enhance
        mask = weights > 0
        vertex_normals[mask] /= weights[mask, np.newaxis]
        
        # Create extreme variations
        spike_factors = np.zeros(len(vertices))
        for i in range(len(vertices)):
            # Combine multiple patterns for organic look
            height_factor = np.cos(vertices[i, 1] * 0.3) * 2
            radial_factor = np.sin(np.arctan2(vertices[i, 0], vertices[i, 2]) * 3)
            random_factor = np.random.uniform(0.8, 2.0)
            
            spike_factors[i] = (height_factor + radial_factor + random_factor) * base_intensity

        # Apply dramatic displacement
        enhanced_vertices = vertices.copy()
        enhanced_vertices += vertex_normals * spike_factors[:, np.newaxis] * base_intensity
        
        return enhanced_vertices

    @staticmethod
    def enhance_features(vertices, faces):
        """Apply dramatic feature enhancement"""
        # Calculate mesh properties
        edges = set()
        for face in faces:
            for i in range(3):
                edge = tuple(sorted([face[i], face[(i + 1) % 3]]))
                edges.add(edge)
        
        # Create sharp features along edges
        edge_vertices = set()
        for edge in edges:
            edge_vertices.update(edge)
        
        # Enhanced vertex positions
        enhanced_vertices = vertices.copy()
        
        # Apply dramatic transformations
        for i in range(len(vertices)):
            if i in edge_vertices:
                # Enhance edge features
                factor = np.random.uniform(1.5, 2.5)
                enhanced_vertices[i] += (vertices[i] - np.mean(vertices, axis=0)) * factor
            else:
                # Add subtle variation to non-edge vertices
                factor = np.random.uniform(0.8, 1.2)
                enhanced_vertices[i] *= factor

        return enhanced_vertices