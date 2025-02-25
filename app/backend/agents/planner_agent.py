from crewai import Agent, Task
from typing import Dict, Any, Optional
from tools.planning_tool import PlanningTool
from prompts.prompt import PLANNER_AGENT
from config import DEFAULT_LLM

class PlannerAgent:
    def __init__(self):
        self.planning_tool = PlanningTool()
    
    def get_agent(self) -> Agent:
        """
        Create and return the planner agent with configuration
        """
        return Agent(
            role=PLANNER_AGENT["role"],
            goal=PLANNER_AGENT["goal"],
            backstory=PLANNER_AGENT["backstory"],
            llm=DEFAULT_LLM,
            verbose=True,
            memory=True,
            respect_context_window=True,
            max_rpm=10
        )
    
    def create_planning_task(self, mesh_data: Dict[str, Any], question: Optional[str] = None) -> Task:
        """
        Create planning task for VTK-based problems
        """
        description = f"""Analyze the provided mesh data and develop a solution strategy.
        Mesh information:
        - Number of points: {mesh_data['num_points']}
        - Number of cells: {mesh_data['num_cells']}
        """
        
        if question:
            description += f"\nAddress the specific question: {question}"
        
        return Task(
            description=description,
            agent=self.get_agent()
        )
    
    def create_text_planning_task(self, question: str) -> Task:
        """
        Create planning task for text-based questions
        """
        return Task(
            description=f"""Analyze the following question about heat equations and 
            develop a solution strategy: {question}""",
            agent=self.get_agent()
        ) 