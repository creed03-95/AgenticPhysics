from langchain.tools import Tool
import numpy as np
from typing import Dict, Any
import dolfin as df
import matplotlib.pyplot as plt
from pathlib import Path

class FenicsTool:
    def solve_heat_equation(self, mesh_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve steady-state heat equation using FEniCS
        """
        try:
            # Create mesh from data
            points = mesh_data['coordinates']
            cells = mesh_data['connectivity']
            
            # Create FEniCS mesh
            mesh = df.Mesh()
            editor = df.MeshEditor()
            editor.open(mesh, "triangle", 2, 2)  # 2D triangular mesh
            
            # Add vertices
            editor.init_vertices(len(points))
            for i, point in enumerate(points):
                editor.add_vertex(i, point[:2])  # Use only x, y coordinates
            
            # Add cells
            editor.init_cells(len(cells))
            for i, cell in enumerate(cells):
                editor.add_cell(i, cell[:3])  # Use first 3 points for triangles
            
            editor.close()
            
            # Define function space
            V = df.FunctionSpace(mesh, "P", 1)
            
            # Define boundary conditions
            def boundary(x, on_boundary):
                return on_boundary
            
            bc = df.DirichletBC(V, df.Constant(0.0), boundary)
            
            # Define variational problem
            u = df.TrialFunction(V)
            v = df.TestFunction(V)
            f = df.Constant(1.0)  # Source term
            a = df.dot(df.grad(u), df.grad(v))*df.dx
            L = f*v*df.dx
            
            # Solve
            u = df.Function(V)
            df.solve(a == L, u, bc)
            
            # Extract solution
            solution = u.vector().get_local()
            
            # Create visualization
            plt.figure(figsize=(10, 8))
            plot = df.plot(u)
            plt.colorbar(plot)
            plt.title("Steady-State Heat Distribution")
            
            # Save plot
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            plt.savefig(output_dir / "heat_distribution.png")
            plt.close()
            
            return {
                "solution": solution.tolist(),
                "plot_path": str(output_dir / "heat_distribution.png")
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_tool(self) -> Tool:
        """
        Create and return the FEniCS tool
        """
        return Tool(
            name="fenics_solver",
            func=self.solve_heat_equation,
            description="""Use this tool to solve steady-state heat equations using
            the FEniCS finite element library. Provide mesh data as input."""
        ) 