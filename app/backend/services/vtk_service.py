import vtk
import numpy as np
from typing import Dict, Any

class VTKService:
    def parse_vtk_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse VTK file and extract mesh data, supporting both structured and unstructured grids
        """
        # First try reading as structured grid
        reader = vtk.vtkStructuredGridReader()
        reader.SetFileName(file_path)
        reader.Update()
        
        grid = reader.GetOutput()
        if not grid or grid.GetNumberOfPoints() == 0:
            # If not structured, try unstructured
            reader = vtk.vtkUnstructuredGridReader()
            reader.SetFileName(file_path)
            reader.Update()
            grid = reader.GetOutput()
        
        if not grid or grid.GetNumberOfPoints() == 0:
            raise ValueError("Could not read VTK file as either structured or unstructured grid")
        
        # Extract point coordinates
        points = grid.GetPoints()
        num_points = points.GetNumberOfPoints()
        coordinates = np.zeros((num_points, 3))
        for i in range(num_points):
            coordinates[i] = points.GetPoint(i)
        
        # Extract cells/connectivity
        num_cells = grid.GetNumberOfCells()
        connectivity = []
        for i in range(num_cells):
            cell = grid.GetCell(i)
            cell_points = [cell.GetPointId(j) for j in range(cell.GetNumberOfPoints())]
            connectivity.append(cell_points)
        
        # Extract any point data (temperature, etc.)
        point_data = {}
        pd = grid.GetPointData()
        for i in range(pd.GetNumberOfArrays()):
            array = pd.GetArray(i)
            name = array.GetName()
            data = np.array([array.GetValue(j) for j in range(array.GetNumberOfTuples())])
            point_data[name] = data
        
        # Get grid dimensions if structured
        dimensions = None
        if isinstance(grid, vtk.vtkStructuredGrid):
            dimensions = grid.GetDimensions()
            dimensions = list(dimensions)  # Convert to list for JSON serialization
        
        # Create the mesh data dictionary with proper types
        mesh_data = {
            "coordinates": coordinates.tolist(),  # Convert numpy array to list
            "connectivity": connectivity,
            "point_data": {k: v.tolist() for k, v in point_data.items()},  # Convert numpy arrays to lists
            "num_points": int(num_points),  # Ensure integer type
            "num_cells": int(num_cells),  # Ensure integer type
            "dimensions": dimensions,
            "is_structured": isinstance(grid, vtk.vtkStructuredGrid)
        }
        
        return mesh_data 

    def compute_temperature_metrics(self, mesh_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute detailed temperature metrics from mesh data
        Returns coordinates of maximum temperature and other relevant metrics
        """
        try:
            # Get temperature data and coordinates
            temperature_data = None
            for key, data in mesh_data['point_data'].items():
                if 'temp' in key.lower():  # Match any temperature-related field
                    temperature_data = np.array(data)
                    break
            
            if temperature_data is None:
                raise ValueError("No temperature data found in the mesh")
                
            coordinates = np.array(mesh_data['coordinates'])
            
            # Find maximum temperature location
            max_temp_idx = np.argmax(temperature_data)
            max_temp = float(temperature_data[max_temp_idx])
            max_temp_coords = coordinates[max_temp_idx].tolist()
            
            # Compute basic statistical metrics
            temp_stats = {
                'min': float(np.min(temperature_data)),
                'max': float(np.max(temperature_data)),
                'mean': float(np.mean(temperature_data)),
                'median': float(np.median(temperature_data)),
                'std_dev': float(np.std(temperature_data))
            }
            
            # Identify regions with high temperature gradients
            if mesh_data['is_structured'] and mesh_data['dimensions']:
                dims = mesh_data['dimensions']
                shaped_temp = temperature_data.reshape(dims[2], dims[1], dims[0])
                gradients = np.gradient(shaped_temp)
                gradient_magnitude = np.sqrt(sum(g*g for g in gradients))
                max_gradient_idx = np.unravel_index(np.argmax(gradient_magnitude), gradient_magnitude.shape)
                max_gradient_value = float(gradient_magnitude[max_gradient_idx])
            else:
                max_gradient_value = None
                max_gradient_idx = None
            
            return {
                'maximum_temperature': {
                    'value': max_temp,
                    'coordinates': max_temp_coords,
                },
                'temperature_statistics': temp_stats,
                'gradient_info': {
                    'max_gradient': max_gradient_value,
                    'max_gradient_location': max_gradient_idx if max_gradient_idx is not None else None
                }
            }
            
        except Exception as e:
            raise ValueError(f"Error computing temperature metrics: {str(e)}") 