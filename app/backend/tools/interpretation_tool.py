from langchain.tools import Tool
import numpy as np
from typing import Dict, Any
from pathlib import Path

class InterpretationTool:
    def analyze_solution(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze and interpret the solution data
        """
        try:
            analysis = {}
            
            if "solution" in data:
                solution = np.array(data["solution"])
                
                # Basic statistics
                analysis["statistics"] = {
                    "max_temperature": float(np.max(solution)),
                    "min_temperature": float(np.min(solution)),
                    "average_temperature": float(np.mean(solution)),
                    "temperature_range": float(np.ptp(solution))
                }
                
                # Identify hot spots
                threshold = np.percentile(solution, 90)
                hot_spots = np.where(solution > threshold)
                analysis["hot_spots"] = {
                    "threshold": float(threshold),
                    "count": len(hot_spots[0]),
                    "locations": [
                        {"x": int(x), "y": int(y)} 
                        for x, y in zip(hot_spots[0], hot_spots[1])
                    ][:5]  # List first 5 hot spots
                }
                
                # Temperature gradients
                dx, dy = np.gradient(solution)
                grad_mag = np.sqrt(dx**2 + dy**2)
                analysis["gradients"] = {
                    "max_gradient": float(np.max(grad_mag)),
                    "average_gradient": float(np.mean(grad_mag)),
                    "steepest_region": {
                        "x": int(np.unravel_index(np.argmax(grad_mag), grad_mag.shape)[0]),
                        "y": int(np.unravel_index(np.argmax(grad_mag), grad_mag.shape)[1])
                    }
                }
                
                # Generate interpretation text
                interpretation = f"""
                The steady-state heat distribution analysis reveals:
                
                1. Temperature Range:
                   - Maximum temperature: {analysis['statistics']['max_temperature']:.2f}
                   - Minimum temperature: {analysis['statistics']['min_temperature']:.2f}
                   - Average temperature: {analysis['statistics']['average_temperature']:.2f}
                
                2. Hot Spots:
                   - {analysis['hot_spots']['count']} regions exceed {analysis['hot_spots']['threshold']:.2f}
                   - Most significant hot spots are located at {analysis['hot_spots']['locations'][:3]}
                
                3. Temperature Gradients:
                   - Maximum gradient: {analysis['gradients']['max_gradient']:.2f}
                   - Average gradient: {analysis['gradients']['average_gradient']:.2f}
                   - Steepest temperature change at position {analysis['gradients']['steepest_region']}
                
                Key Insights:
                - The temperature distribution shows {'significant' if analysis['statistics']['temperature_range'] > 1 else 'minimal'} variation
                - Heat flow is {'uniform' if analysis['gradients']['max_gradient'] < 0.5 else 'non-uniform'} across the domain
                - The solution {'has' if analysis['hot_spots']['count'] > 0 else 'does not have'} notable hot spots
                """
                
                analysis["interpretation"] = interpretation
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def interpret_results(self, question: str, metrics: Dict[str, Any], research_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpret results based on metrics, research, and the original question
        """
        try:
            interpretation = {}
            
            # Extract key metrics
            if metrics:
                if "temperature" in metrics:
                    temp_metrics = metrics["temperature"]
                    interpretation["temperature_analysis"] = {
                        "min": float(temp_metrics["min"]),
                        "max": float(temp_metrics["max"]),
                        "mean": float(temp_metrics["mean"]),
                        "range": float(temp_metrics["max"] - temp_metrics["min"])
                    }
                
                if "gradients" in metrics:
                    grad_metrics = metrics["gradients"]
                    interpretation["gradient_analysis"] = {
                        "max_gradient": float(grad_metrics["max_gradient"]),
                        "mean_gradient": float(grad_metrics["mean_gradient"])
                    }
            
            # Generate physical description
            physical_description = []
            
            if "temperature_analysis" in interpretation:
                ta = interpretation["temperature_analysis"]
                physical_description.append(
                    f"The temperature field ranges from {ta['min']:.2f} to {ta['max']:.2f}, "
                    f"with an average of {ta['mean']:.2f}."
                )
            
            if "gradient_analysis" in interpretation:
                ga = interpretation["gradient_analysis"]
                physical_description.append(
                    f"Temperature gradients reach a maximum of {ga['max_gradient']:.2f}, "
                    f"indicating {'strong' if ga['max_gradient'] > 1.0 else 'moderate' if ga['max_gradient'] > 0.5 else 'mild'} "
                    f"heat transfer in some regions."
                )
            
            # Add research insights if available
            if research_results:
                if "key_findings" in research_results:
                    physical_description.append("\nResearch insights:")
                    physical_description.extend([f"- {finding}" for finding in research_results["key_findings"][:3]])
            
            interpretation["physical_description"] = "\n".join(physical_description)
            
            return interpretation
            
        except Exception as e:
            return {"error": str(e), "physical_description": "Could not generate interpretation due to an error."}
    
    def get_tool(self) -> Tool:
        """
        Create and return the interpretation tool
        """
        return Tool(
            name="interpretation_tool",
            func=self.analyze_solution,
            description="""Use this tool to analyze and interpret the heat equation
            solution, providing statistical analysis and physical insights."""
        ) 