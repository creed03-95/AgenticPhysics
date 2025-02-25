from crewai import Agent, Task
from typing import Dict, Any
from tools.fenics_tool import FenicsTool
from tools.numerical_tool import NumericalTool
from prompts.prompt import SOLVER_AGENT, SOLVER_TASK_TEMPLATE
from config import DEFAULT_LLM

class SolverAgent:
    def __init__(self):
        self.fenics_tool = FenicsTool()
        self.numerical_tool = NumericalTool()
    
    def get_agent(self) -> Agent:
        """
        Create and return the solver agent with configuration
        """
        return Agent(
            role=SOLVER_AGENT["role"],
            goal=SOLVER_AGENT["goal"],
            backstory=SOLVER_AGENT["backstory"],
            tools=[
                self.fenics_tool.get_tool(),
                self.numerical_tool.get_tool()
            ],
            llm=DEFAULT_LLM,
            verbose=True,
            memory=True,
            respect_context_window=True,
            max_rpm=10
        )
    
    def create_text_solving_task(self, question: str, planner_output: str = "") -> Task:
        """
        Create solving task for text-based questions
        """
        return Task(
            description=SOLVER_TASK_TEMPLATE.format(
                question=question,
                planner_output=planner_output
            ),
            agent=self.get_agent()
        ) 