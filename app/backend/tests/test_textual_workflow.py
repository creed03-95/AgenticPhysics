from app.backend.core.workflow_manager import WorkflowManager

def test_heat_equation_analysis():
    """
    Test analyzing a complex heat equation problem with boundary conditions
    """
    print("\nTesting heat equation analysis workflow...")
    
    # Test question about heat equation and boundary conditions
    question = """Analyze this steady-state heat equation solution T(x,y) = x^2+y^2 in a unit square domain and tell 
    what physical significance does the boundary condition u(0,y)=0 have in the context of heat diffusion on the unit square mesh?"""
    
    try:
        # Initialize workflow manager
        workflow_manager = WorkflowManager()
        
        # Execute text workflow
        print("\nExecuting text workflow with question:")
        print(question)
        print("\nProcessing...")
        
        result = workflow_manager.execute_text_workflow(question)
        
        print("\nWorkflow Result:")
        print(result)
        print("\nText workflow test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError in text workflow: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting textual workflow test...")
    
    # Run test
    success = test_heat_equation_analysis()
    
    # Report results
    print("\nTest Results:")
    print(f"Heat Equation Analysis: {'✓' if success else '✗'}")
    
    # Exit with appropriate status
    import sys
    sys.exit(0 if success else 1) 