from langchain.tools import Tool
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve
from typing import Dict, Any
import matplotlib.pyplot as plt
from pathlib import Path

class NumericalTool:
    def solve_finite_difference(self, nx: int = 50, ny: int = 50) -> Dict[str, Any]:
        """
        Solve 2D steady-state heat equation using finite difference method
        """
        try:
            # Create grid
            x = np.linspace(0, 1, nx)
            y = np.linspace(0, 1, ny)
            dx = x[1] - x[0]
            dy = y[1] - y[0]
            
            # Initialize matrices
            N = nx * ny
            A = np.zeros((N, N))
            b = np.zeros(N)
            
            # Fill matrices using 5-point stencil
            for i in range(nx):
                for j in range(ny):
                    k = i + j*nx
                    
                    if i == 0 or i == nx-1 or j == 0 or j == ny-1:
                        # Boundary conditions
                        A[k, k] = 1
                        b[k] = 0
                    else:
                        # Interior points
                        A[k, k] = -4
                        A[k, k-1] = 1
                        A[k, k+1] = 1
                        A[k, k-nx] = 1
                        A[k, k+nx] = 1
                        b[k] = -1  # Source term
            
            # Convert to sparse matrix
            A_sparse = csr_matrix(A)
            
            # Solve system
            u = spsolve(A_sparse, b)
            
            # Reshape solution to 2D
            u_2d = u.reshape((ny, nx))
            
            # Create visualization
            plt.figure(figsize=(10, 8))
            plt.imshow(u_2d, cmap='hot', origin='lower')
            plt.colorbar(label='Temperature')
            plt.title("Steady-State Heat Distribution (Finite Difference)")
            plt.xlabel("x")
            plt.ylabel("y")
            
            # Save plot
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            plot_path = output_dir / "heat_distribution_fd.png"
            plt.savefig(plot_path)
            plt.close()
            
            return {
                "solution": u_2d.tolist(),
                "plot_path": str(plot_path)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_tool(self) -> Tool:
        """
        Create and return the numerical tool
        """
        return Tool(
            name="numerical_solver",
            func=self.solve_finite_difference,
            description="""Use this tool to solve steady-state heat equations using
            finite difference methods. Specify grid dimensions as input."""
        ) 