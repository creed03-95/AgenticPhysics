from crewai import Agent, Task
from typing import Dict, Any, Optional
from prompts.prompt import MANAGER_AGENT
from config import DEFAULT_LLM

class ManagerAgent:
    def get_agent(self) -> Agent:
        """
        Create and return the manager agent with configuration
        """
        return Agent(
            role=MANAGER_AGENT["role"],
            goal=MANAGER_AGENT["goal"],
            backstory=MANAGER_AGENT["backstory"],
            llm=DEFAULT_LLM,
            verbose=True,
            memory=True,
            respect_context_window=True,
            max_rpm=10
        )
    
    def determine_workflow(self, question: str, mesh_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Determine which workflow to use based on input
        """
        # If mesh data is provided, always use VTK workflow
        if mesh_data is not None:
            return {
                "workflow_type": "vtk",
                "reasoning": "VTK file provided with question, using VTK analysis workflow."
            }
        
        # For text-only questions, use text workflow
        return {
            "workflow_type": "text",
            "reasoning": "Text-only question provided, using theoretical analysis workflow."
        } 