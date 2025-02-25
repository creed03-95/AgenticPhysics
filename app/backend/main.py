from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from core.workflow_manager import WorkflowManager
from schemas.request_models import TextualQuestion
from services.vtk_service import VTKService
from utils.file_handler import FileHandler
from agents.manager_agent import ManagerAgent

app = FastAPI(title="Heat Equation Solver API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/solve")
async def solve_heat_equation(
    question: str = Form(...),
    vtk_file: Optional[UploadFile] = File(None)
):
    """
    Unified endpoint for solving heat equation problems
    """
    try:
        manager = ManagerAgent()
        workflow_manager = WorkflowManager()
        
        if vtk_file:
            # Process VTK file if provided
            file_handler = FileHandler()
            vtk_service = VTKService()
            
            vtk_path = await file_handler.save_upload_file(vtk_file)
            mesh_data = vtk_service.parse_vtk_file(vtk_path)
            
            # Determine workflow
            workflow_info = manager.determine_workflow(question, mesh_data)
            
            # Use existing VTK workflow to maintain functionality
            result = workflow_manager.execute_vtk_workflow(mesh_data, question)
            
            return {
                "result": result,
                "workflow_type": workflow_info["workflow_type"],
                "reasoning": workflow_info["reasoning"]
            }
        else:
            # Handle text-only questions
            workflow_info = manager.determine_workflow(question)
            result = workflow_manager.execute_text_workflow(question)
            
            return {
                "result": result,
                "workflow_type": workflow_info["workflow_type"],
                "reasoning": workflow_info["reasoning"]
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/solve/vtk-with-question")
async def solve_vtk_with_question(
    vtk_file: UploadFile = File(...),
    question: str = Form(...)
):
    """
    Endpoint to solve heat equation based on VTK file and question
    """
    try:
        # Initialize services
        file_handler = FileHandler()
        vtk_service = VTKService()
        workflow_manager = WorkflowManager()

        # Save and process VTK file
        vtk_path = await file_handler.save_upload_file(vtk_file)
        mesh_data = vtk_service.parse_vtk_file(vtk_path)

        # Execute workflow
        result = workflow_manager.execute_vtk_workflow(mesh_data, question)
        
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/solve/question")
async def solve_question(question: TextualQuestion):
    """
    Endpoint to solve heat equation based on textual question only
    """
    try:
        workflow_manager = WorkflowManager()
        result = workflow_manager.execute_text_workflow(question.text)
        
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.backend.main:app", host="0.0.0.0", port=8000, reload=True) 