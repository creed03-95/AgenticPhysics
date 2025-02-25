from crewai import Agent, Task
from typing import Dict, Any
import numpy as np
from prompts.prompt import METRICS_AGENT, METRICS_TASK_TEMPLATE
from config import METRICS_LLM
from services.vtk_service import VTKService

class MetricsAgent:
    def get_agent(self) -> Agent:
        """
        Create and return the metrics agent with enhanced configuration
        """
        return Agent(
            role=METRICS_AGENT["role"],
            goal=METRICS_AGENT["goal"],
            backstory=METRICS_AGENT["backstory"],
            llm=METRICS_LLM,
            verbose=True,
            memory=True,  # Enable memory for metrics context
            respect_context_window=True,  # Prevent token limit issues
            max_rpm=10  # Rate limiting for API stability
        )
    
    def analyze_vtk_metrics(self, mesh_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key metrics from VTK data with enhanced temperature analysis
        """
        metrics = {}
        vtk_service = VTKService()
        
        # Basic mesh statistics
        metrics["mesh_stats"] = {
            "num_points": mesh_data["num_points"],
            "num_cells": mesh_data["num_cells"],
            "dimension": len(mesh_data["coordinates"][0]) if mesh_data["coordinates"] else 0
        }
        
        # Enhanced temperature analysis
        try:
            temp_metrics = vtk_service.compute_temperature_metrics(mesh_data)
            metrics["temperature_analysis"] = temp_metrics
        except ValueError as e:
            # If temperature analysis fails, fall back to basic point data analysis
            if "point_data" in mesh_data:
                for field_name, field_data in mesh_data["point_data"].items():
                    data = np.array(field_data) if isinstance(field_data, list) else field_data
                    metrics[field_name] = {
                        "min": float(np.min(data)),
                        "max": float(np.max(data)),
                        "mean": float(np.mean(data)),
                        "std": float(np.std(data))
                    }
        
        return metrics
    
    def create_metrics_task(self, mesh_data: Dict[str, Any], question: str) -> Task:
        """
        Create task for analyzing VTK metrics with enhanced temperature focus
        """
        # First analyze the metrics
        metrics = self.analyze_vtk_metrics(mesh_data)
        
        # Format metrics summary with special attention to temperature data
        metrics_summary = []
        
        # Add mesh statistics
        if "mesh_stats" in metrics:
            metrics_summary.append("Mesh Statistics:")
            for key, value in metrics["mesh_stats"].items():
                metrics_summary.append(f"  - {key}: {value}")
        
        # Add temperature analysis if available
        if "temperature_analysis" in metrics:
            metrics_summary.append("\nTemperature Analysis:")
            temp_analysis = metrics["temperature_analysis"]
            
            # Maximum temperature details
            max_temp = temp_analysis["maximum_temperature"]
            metrics_summary.append(f"  Maximum Temperature:")
            metrics_summary.append(f"    - Value: {max_temp['value']}")
            metrics_summary.append(f"    - Location: {max_temp['coordinates']}")
            
            # Temperature statistics
            metrics_summary.append("\n  Temperature Statistics:")
            for key, value in temp_analysis["temperature_statistics"].items():
                metrics_summary.append(f"    - {key}: {value}")
            
            # Gradient information if available
            if temp_analysis["gradient_info"]["max_gradient"] is not None:
                metrics_summary.append("\n  Gradient Information:")
                metrics_summary.append(f"    - Maximum Gradient: {temp_analysis['gradient_info']['max_gradient']}")
        
        dimensions_str = "x".join(map(str, mesh_data["dimensions"])) if mesh_data.get("dimensions") else "N/A"
        
        return Task(
            description=(
                f"Analyze the temperature distribution in this mesh:\n"
                f"Mesh dimensions: {dimensions_str}\n"
                f"Points: {mesh_data['num_points']}, Cells: {mesh_data['num_cells']}\n"
                f"Question: {question}\n"
                f"Available metrics:\n" + "\n".join(metrics_summary)
            ),
            expected_output=(
                "Provide a clear and specific answer to the question, including:\n"
                "1. Exact numerical values where applicable (e.g., coordinates, temperatures)\n"
                "2. Supporting analysis of temperature distribution\n"
                "3. Physical interpretation of the results\n"
                "4. Relevant boundary conditions and gradients"
            ),
            agent=self.get_agent()
        ) 