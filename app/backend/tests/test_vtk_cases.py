import os
from fastapi.testclient import TestClient
from app.backend.main import app
from app.backend.core.workflow_manager import WorkflowManager

# Create test client
client = TestClient(app)

def test_vtk_analysis():
    """
    Test analyzing a real VTK file with a specific question
    """
    print("\nTesting VTK file analysis with question...")
    
    # Path to your VTK file
    vtk_file_path = "app/backend/tests/data/Case2.vtk"
    
    if not os.path.exists(vtk_file_path):
        print(f"\nPlease place your VTK file at: {os.path.abspath(vtk_file_path)}")
        return False
    
    # Question about the VTK data
    question = """
    Analyze the temperature distribution in this mesh:
    1. Explain why the temperature is zero at both x=0 and x=1, and what this means physically.
    2. At what coordinates does the maximum temperature occur, and what determines this location?
    3. What are the maximum and minimum temperature regions?
    4. Are there any significant temperature gradients?
    5. What physical phenomena might explain these patterns?
    """
    
    try:
        with open(vtk_file_path, "rb") as vtk_file:
            files = {"vtk_file": ("test.vtk", vtk_file, "application/octet-stream")}
            data = {"question": (None, question)}  # Format for Form data
            response = client.post(
                "/solve/vtk-with-question",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            print("\nVTK Analysis Result:")
            print(response.json()["result"])
            print("\nVTK analysis test completed successfully!")
            return True
        else:
            print(f"\nError: API returned status code {response.status_code}")
            print(response.json())
            return False
            
    except Exception as e:
        print(f"\nError in VTK analysis: {str(e)}")
        return False

def test_heat_equation_interpretation():
    """
    Test interpreting a heat equation problem
    """
    print("\nTesting heat equation interpretation...")
    
    # Complex heat equation question
    question = {
        "text": """
        Consider the 2D heat equation:
        ∂T/∂t = α(∂²T/∂x² + ∂²T/∂y²)
        
        For a square metal plate with:
        - Initial temperature: T(x,y,0) = 20°C
        - Boundary conditions: 
          - Left edge: T(0,y,t) = 100°C
          - Right edge: T(L,y,t) = 20°C
          - Top and bottom: Insulated
        
        Please explain:
        1. What does this equation represent physically?
        2. How will the temperature distribute over time?
        3. Where will the highest temperature gradients occur?
        4. What real-world applications might this scenario represent?
        """
    }
    
    try:
        response = client.post("/solve/question", json=question)
        
        if response.status_code == 200:
            print("\nHeat Equation Interpretation Result:")
            print(response.json()["result"])
            print("\nHeat equation interpretation test completed successfully!")
            return True
        else:
            print(f"\nError: API returned status code {response.status_code}")
            print(response.json())
            return False
            
    except Exception as e:
        print(f"\nError in heat equation interpretation: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting real-world test cases...")
    
    # Run tests
    vtk_success = test_vtk_analysis()
    equation_success = test_heat_equation_interpretation()
    
    # Report results
    print("\nTest Results:")
    print(f"VTK Analysis: {'✓' if vtk_success else '✗'}")
    print(f"Heat Equation Interpretation: {'✓' if equation_success else '✗'}")
    
    # Exit with appropriate status
    import sys
    sys.exit(0 if vtk_success and equation_success else 1) 