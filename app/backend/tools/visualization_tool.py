from langchain.tools import Tool
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any, List

class VisualizationTool:
    def create_visualizations(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create various visualizations for the solution data
        """
        try:
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            plots = {}
            
            if "solution" in data:
                solution = np.array(data["solution"])
                
                # 2D contour plot
                plt.figure(figsize=(10, 8))
                plt.contourf(solution, cmap='hot')
                plt.colorbar(label='Temperature')
                plt.title("Temperature Distribution (Contour)")
                plt.xlabel("x")
                plt.ylabel("y")
                contour_path = output_dir / "temperature_contour.png"
                plt.savefig(contour_path)
                plt.close()
                plots["contour"] = str(contour_path)
                
                # 3D surface plot
                fig = plt.figure(figsize=(12, 8))
                ax = fig.add_subplot(111, projection='3d')
                x = np.arange(solution.shape[1])
                y = np.arange(solution.shape[0])
                X, Y = np.meshgrid(x, y)
                surf = ax.plot_surface(X, Y, solution, cmap='hot')
                plt.colorbar(surf)
                ax.set_title("Temperature Distribution (3D)")
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.set_zlabel("Temperature")
                surface_path = output_dir / "temperature_surface.png"
                plt.savefig(surface_path)
                plt.close()
                plots["surface"] = str(surface_path)
                
                # Temperature profile along centerline
                plt.figure(figsize=(10, 6))
                center_idx = solution.shape[0] // 2
                plt.plot(solution[center_idx, :])
                plt.title("Temperature Profile along Centerline")
                plt.xlabel("Position")
                plt.ylabel("Temperature")
                plt.grid(True)
                profile_path = output_dir / "temperature_profile.png"
                plt.savefig(profile_path)
                plt.close()
                plots["profile"] = str(profile_path)
            
            return plots
            
        except Exception as e:
            return {"error": str(e)}
    
    def suggest_visualizations(self, metrics: Dict[str, Any], interpretation: Dict[str, Any]) -> List[str]:
        """
        Suggest appropriate visualizations based on metrics and interpretation
        """
        suggestions = []
        
        # Check temperature distribution characteristics
        if metrics.get("temperature"):
            temp_data = np.array(metrics["temperature"])  # Convert list to numpy array
            temp_range = np.ptp(temp_data)
            if temp_range > 0:
                suggestions.append(
                    "2D contour plot to visualize the overall temperature distribution"
                )
                suggestions.append(
                    "3D surface plot to better understand the temperature variations"
                )
        
        # Check for gradients
        if metrics.get("gradients"):
            grad_data = np.array(metrics["gradients"])  # Convert list to numpy array
            grad_max = np.max(grad_data)
            if grad_max > 0.5:  # Significant gradients
                suggestions.append(
                    "Vector field plot to show temperature gradient directions and magnitudes"
                )
                suggestions.append(
                    "Gradient magnitude contour plot to identify regions of rapid temperature change"
                )
        
        # Check for specific features mentioned in interpretation
        if interpretation:
            if "hot_spots" in str(interpretation):
                suggestions.append(
                    "Highlighted contour plot marking identified hot spots"
                )
            if "boundary" in str(interpretation):
                suggestions.append(
                    "Boundary condition visualization showing temperature constraints"
                )
            if "profile" in str(interpretation) or "cross-section" in str(interpretation):
                suggestions.append(
                    "Temperature profile plots along key cross-sections"
                )
        
        # If no specific suggestions were made, provide default ones
        if not suggestions:
            suggestions = [
                "Basic 2D contour plot of temperature distribution",
                "Temperature profile along the domain centerline",
                "3D surface plot for overall temperature visualization"
            ]
        
        return suggestions
    
    def get_tool(self) -> Tool:
        """
        Create and return the visualization tool
        """
        return Tool(
            name="visualization_tool",
            func=self.create_visualizations,
            description="""Use this tool to create various visualizations of the
            heat equation solution, including contour plots, 3D surface plots,
            and temperature profiles."""
        ) 