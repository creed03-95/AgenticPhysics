from langchain.tools import Tool
from typing import Dict, Any, Optional
import json

class PlanningTool:
    def create_solution_plan(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a solution plan for the heat equation problem
        """
        try:
            plan = {
                "steps": [],
                "methods": {},
                "parameters": {}
            }
            
            # Analyze problem type
            if "mesh_data" in problem_data:
                # VTK-based problem
                mesh_data = problem_data["mesh_data"]
                plan["problem_type"] = "mesh_based"
                plan["steps"] = [
                    "1. Validate mesh data and boundary conditions",
                    "2. Set up finite element discretization",
                    "3. Assemble system matrices",
                    "4. Apply boundary conditions",
                    "5. Solve linear system",
                    "6. Post-process results"
                ]
                plan["methods"] = {
                    "discretization": "finite_element",
                    "solver": "direct_sparse",
                    "element_type": "P1"
                }
                plan["parameters"] = {
                    "mesh_points": mesh_data.get("num_points", 0),
                    "mesh_cells": mesh_data.get("num_cells", 0)
                }
            else:
                # Text-based problem
                question = problem_data.get("question", "")
                plan["problem_type"] = "analytical"
                plan["steps"] = [
                    "1. Analyze problem requirements",
                    "2. Set up computational domain",
                    "3. Choose numerical method",
                    "4. Implement solution",
                    "5. Validate results"
                ]
                plan["methods"] = {
                    "discretization": "finite_difference",
                    "solver": "sparse_iterative",
                    "grid_type": "uniform"
                }
                plan["parameters"] = {
                    "grid_size": [50, 50],
                    "tolerance": 1e-6,
                    "max_iterations": 1000
                }
            
            # Add analysis requirements
            plan["analysis"] = {
                "required_plots": [
                    "temperature_distribution",
                    "gradient_magnitude",
                    "convergence_history"
                ],
                "metrics": [
                    "max_temperature",
                    "min_temperature",
                    "average_temperature",
                    "temperature_gradients"
                ]
            }
            
            return plan
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_tool(self) -> Tool:
        """
        Create and return the planning tool
        """
        return Tool(
            name="solution_planner",
            func=self.create_solution_plan,
            description="""Use this tool to create a detailed solution plan for
            heat equation problems, including steps, methods, and parameters."""
        ) 