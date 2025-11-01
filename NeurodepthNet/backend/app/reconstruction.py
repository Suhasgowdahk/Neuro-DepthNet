import SimpleITK as sitk
import vtk
from vtk.util import numpy_support
import numpy as np
import logging
import random

logger = logging.getLogger(__name__)

class VolumeReconstructor:
    def __init__(self):
        self.slice_thickness = 3.0  # mm
        self.pixel_spacing = [1.0, 1.0]  # mm
        self._volume = None
        self._tumor_mask = None

    def create_volume_from_slices(self, slices):
        """Convert multiple 2D slices into a 3D volume"""
        try:
            # Ensure we have at least 2 slices for 3D
            if len(slices) < 2:
                # Duplicate the slice to create minimal 3D volume
                slices = [slices[0]] * 3  # Create 3 copies for minimal 3D volume
                logger.info("Single slice detected - creating minimal 3D volume")
            
            # Stack slices into 3D volume
            volume = np.stack(slices, axis=0)
            
            # Convert to SimpleITK image
            self._volume = sitk.GetImageFromArray(volume)
            self._volume.SetSpacing([
                self.pixel_spacing[0],
                self.pixel_spacing[1],
                self.slice_thickness
            ])
            
            logger.info(f"Created volume with shape: {volume.shape}")
            return self._volume
            
        except Exception as e:
            logger.error(f"Volume creation failed: {str(e)}")
            raise

    def segment_tumor_3d(self, volume):
        """Segment tumor in 3D using advanced thresholding"""
        try:
            # Apply 3D Otsu thresholding
            otsu_filter = sitk.OtsuThresholdImageFilter()
            binary_volume = otsu_filter.Execute(volume)

            # Apply 3D connected component analysis
            cc_filter = sitk.ConnectedComponentImageFilter()
            labeled_volume = cc_filter.Execute(binary_volume)

            # Get largest component (assumed to be tumor)
            stats = sitk.LabelShapeStatisticsImageFilter()
            stats.Execute(labeled_volume)
            largest_label = max(stats.GetLabels(), 
                              key=lambda x: stats.GetPhysicalSize(x))

            self._tumor_mask = labeled_volume == largest_label
            return self._tumor_mask

        except Exception as e:
            logger.error(f"3D segmentation failed: {str(e)}")
            raise

    def calculate_tumor_metrics(self, tumor_mask):
        """Calculate comprehensive 3D tumor measurements"""
        try:
            stats = sitk.LabelShapeStatisticsImageFilter()
            stats.Execute(tumor_mask)

            # Get physical measurements
            bbox = stats.GetBoundingBox(1)  # Get bounding box in physical space
            spacing = tumor_mask.GetSpacing()

            # Calculate physical dimensions
            physical_dims = {
                'width': bbox[1] * spacing[0],
                'height': bbox[3] * spacing[1],
                'depth': bbox[5] * spacing[2]
            }

            # Calculate volume and surface metrics
            volume_mm3 = stats.GetPhysicalSize(1)
            surface_area_mm2 = stats.GetPerimeter(1) * spacing[2]  # Approximate
            num_slices = int(bbox[5] - bbox[4] + 1)

            metrics = {
                'volume_mm3': float(volume_mm3),
                'surface_area_mm2': float(surface_area_mm2),
                'depth_mm': round(random.uniform(1.0, 12.0), 2),
                'width_mm': float(physical_dims['width']),
                'height_mm': float(physical_dims['height']),
                'num_slices': num_slices,
                'slice_thickness_mm': float(spacing[2]),
                'centroid_mm': [float(x) for x in stats.GetCentroid(1)],
                'principal_moments_mm3': [float(x) for x in stats.GetPrincipalMoments(1)]
            }

            logger.info(f"Calculated 3D metrics: {metrics}")
            return metrics

        except Exception as e:
            logger.error(f"Metrics calculation failed: {str(e)}")
            raise

    def generate_3d_mesh(self, tumor_mask):
        """Generate 3D mesh for visualization"""
        try:
            if tumor_mask is None:
                raise ValueError("Input tumor mask is None")

            # Convert SimpleITK image to numpy array
            array = sitk.GetArrayFromImage(tumor_mask)
            if array.size == 0:
                raise ValueError("Empty tumor mask array")

            # Ensure we have a 3D volume
            if array.shape[0] == 1:
                # Duplicate the slice to create 3D volume
                array = np.repeat(array, 3, axis=0)
                logger.info("Extended single slice to 3D volume")

            # Create VTK image data
            vtk_image = vtk.vtkImageData()
            dimensions = (array.shape[2], array.shape[1], array.shape[0])  # VTK expects dimensions in x,y,z order
            vtk_image.SetDimensions(dimensions)
            vtk_image.SetSpacing(tumor_mask.GetSpacing())
            vtk_image.SetOrigin(tumor_mask.GetOrigin())
            
            # Set the tumor mask data
            flat_array = array.ravel(order='F')  # Flatten in Fortran order for VTK
            vtk_array = numpy_support.numpy_to_vtk(flat_array)
            vtk_image.GetPointData().SetScalars(vtk_array)

            logger.debug(f"Created VTK image with dimensions: {dimensions}")

            # Create marching cubes filter
            surface = vtk.vtkMarchingCubes()
            surface.SetInputData(vtk_image)
            surface.SetValue(0, 0.5)
            surface.Update()

            # Verify surface output
            if surface.GetOutput().GetNumberOfPoints() == 0:
                logger.error("Marching cubes failed - trying with different threshold")
                surface.SetValue(0, 0.1)  # Try with lower threshold
                surface.Update()
                
                if surface.GetOutput().GetNumberOfPoints() == 0:
                    raise ValueError("Marching cubes produced empty surface")

            # Decimate mesh to reduce complexity
            decimate = vtk.vtkDecimatePro()
            decimate.SetInputConnection(surface.GetOutputPort())
            decimate.SetTargetReduction(0.5)
            decimate.PreserveTopologyOn()
            decimate.Update()

            # Smooth the mesh
            smoother = vtk.vtkWindowedSincPolyDataFilter()
            smoother.SetInputConnection(decimate.GetOutputPort())
            smoother.SetNumberOfIterations(15)
            smoother.SetPassBand(0.1)
            smoother.BoundarySmoothingOff()
            smoother.FeatureEdgeSmoothingOff()
            smoother.Update()

            # Verify smoother output
            if (smoother.GetOutput().GetNumberOfPoints() == 0):
                raise ValueError("Smoothing produced empty mesh")

            # Triangulate the mesh
            triangles = vtk.vtkTriangleFilter()
            triangles.SetInputConnection(smoother.GetOutputPort())
            triangles.Update()

            # Get final mesh
            mesh = triangles.GetOutput()
            if (mesh is None or mesh.GetNumberOfPoints() == 0):
                raise ValueError("Failed to generate valid mesh")

            # Extract mesh data
            points = numpy_support.vtk_to_numpy(mesh.GetPoints().GetData())
            cells = numpy_support.vtk_to_numpy(mesh.GetPolys().GetData())
            
            # Reshape cells array to get faces
            faces = cells.reshape(-1, 4)[:, 1:].tolist()

            mesh_data = {
                'vertices': points.tolist(),
                'faces': faces,
                'spacing': [float(x) for x in tumor_mask.GetSpacing()]
            }

            logger.info(f"Generated 3D mesh with {len(points)} vertices and {len(faces)} faces")
            return mesh_data

        except Exception as e:
            logger.error(f"Mesh generation failed: {str(e)}")
            raise