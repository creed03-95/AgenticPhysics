from crewai import Crew, Process, Task
from typing import Dict, Any, Optional, List

from app.backend.agents.research_agent import ResearchAgent
from app.backend.agents.metrics_agent import MetricsAgent
from app.backend.agents.summarizer_agent import SummarizerAgent
from app.backend.agents.manager_agent import ManagerAgent
from app.backend.agents.planner_agent import PlannerAgent
from app.backend.agents.solver_agent import SolverAgent
from app.backend.prompts.prompt import (
    PLANNER_TASK_TEMPLATE,
    SOLVER_TASK_TEMPLATE
)

class WorkflowManager:
    def __init__(self):
        self.metrics_agent = MetricsAgent()
        self.research_agent = ResearchAgent()
        self.summarizer_agent = SummarizerAgent()
        self.manager_agent = ManagerAgent()
        self.planner_agent = PlannerAgent()
        self.solver_agent = SolverAgent()
    
    def execute_vtk_workflow(self, mesh_data: Dict[str, Any], question: str) -> str:
        """
        Execute workflow for VTK file with question
        """
        # Create metrics task
        metrics_task = Task(
            description=(
                f"Analyze the temperature distribution in this mesh:\n"
                f"Points: {mesh_data['num_points']}, Cells: {mesh_data['num_cells']}\n"
                f"Question: {question}\n"
                "Provide detailed analysis of temperature patterns and gradients."
            ),
            expected_output=(
                "1. Mesh statistics\n"
                "2. Temperature distribution analysis\n"
                "3. Gradient patterns\n"
                "4. Initial physical interpretation"
            ),
            agent=self.metrics_agent.get_agent()
        )
        
        # Create research task with metrics context
        research_task = Task(
            description=(
                f"Analyze the following heat equation question using metrics data:\n{question}\n"
                "Focus on:\n"
                "1. Physical interpretation of temperature patterns\n"
                "2. Heat equation theory application\n"
                "3. Numerical methods relevance\n"
                "4. Boundary conditions analysis"
            ),
            expected_output=(
                "1. Theoretical foundation\n"
                "2. Physical phenomena explanation\n"
                "3. Connection to numerical methods\n"
                "4. Practical implications"
            ),
            agent=self.research_agent.get_agent(),
            context=[metrics_task]
        )
        
        # Create summary task with both contexts
        summary_task = Task(
            description=(
                f"Create comprehensive summary addressing:\n{question}\n"
                "Combine metrics analysis and theoretical research."
            ),
            expected_output=(
                "1. Clear problem statement\n"
                "2. Analysis methodology\n"
                "3. Results interpretation\n"
                "4. Physical significance\n"
                "5. Practical implications"
            ),
            agent=self.summarizer_agent.get_agent(),
            context=[metrics_task, research_task]
        )
        
        # Create crew with sequential process
        crew = Crew(
            agents=[
                self.metrics_agent.get_agent(),
                self.research_agent.get_agent(),
                self.summarizer_agent.get_agent()
            ],
            tasks=[metrics_task, research_task, summary_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the workflow
        result = crew.kickoff()
        return result
    
    def execute_text_workflow(self, question: str) -> str:
        """
        Execute workflow for textual question only
        """
        # Create and execute manager task first
        manager_task = Task(
            description=(
                f"Analyze this heat equation question:\n{question}\n"
                "Determine:\n"
                "1. Question type and complexity\n"
                "2. Required mathematical approach\n"
                "3. Solution methodology"
            ),
            expected_output=(
                "1. Question classification\n"
                "2. Mathematical concepts needed\n"
                "3. Recommended approach\n"
                "4. Analysis requirements"
            ),
            agent=self.manager_agent.get_agent()
        )
        
        # Execute manager task first
        manager_crew = Crew(
            agents=[self.manager_agent.get_agent()],
            tasks=[manager_task],
            process=Process.sequential,
            verbose=True
        )
        manager_crew.kickoff()
        
        # Create and execute planner task with manager's analysis
        planner_task = Task(
            description=PLANNER_TASK_TEMPLATE.format(
                question=question,
                manager_analysis=manager_task.output if manager_task.output else "No analysis available yet"
            ),
            expected_output=(
                "1. Detailed solution plan\n"
                "2. Mathematical methods\n"
                "3. Key equations and steps\n"
                "4. Validation criteria"
            ),
            agent=self.planner_agent.get_agent(),
            context=[manager_task]
        )
        
        planner_crew = Crew(
            agents=[self.planner_agent.get_agent()],
            tasks=[planner_task],
            process=Process.sequential,
            verbose=True
        )
        planner_crew.kickoff()
        
        # Create solver task with planning context
        solver_task = Task(
            description=SOLVER_TASK_TEMPLATE.format(
                question=question,
                planner_output=planner_task.output if planner_task.output else "No plan available yet"
            ),
            expected_output=(
                "1. Complete solution\n"
                "2. Step-by-step implementation\n"
                "3. Key results\n"
                "4. Validation proof"
            ),
            agent=self.solver_agent.get_agent(),
            context=[manager_task, planner_task]
        )
        
        # Create research task with solution context
        research_task = Task(
            description=(
                f"Research this heat equation problem:\n{question}\n"
                "Based on the solution, focus on:\n"
                "1. Theoretical foundations\n"
                "2. Similar solved problems\n"
                "3. Applicable methods"
            ),
            expected_output=(
                "1. Theoretical background\n"
                "2. Relevant examples\n"
                "3. Method justification\n"
                "4. Key references"
            ),
            agent=self.research_agent.get_agent(),
            context=[manager_task, planner_task, solver_task]
        )
        
        # Create summary task with all context
        summary_task = Task(
            description=(
                f"Create comprehensive summary addressing:\n{question}\n"
                "Synthesize all analyses and provide clear explanation."
            ),
            expected_output=(
                "1. Problem overview\n"
                "2. Solution approach\n"
                "3. Key findings\n"
                "4. Practical implications\n"
                "5. Final recommendations"
            ),
            agent=self.summarizer_agent.get_agent(),
            context=[manager_task, planner_task, solver_task, research_task]
        )
        
        # Create final crew with remaining tasks
        final_crew = Crew(
            agents=[
                self.solver_agent.get_agent(),
                self.research_agent.get_agent(),
                self.summarizer_agent.get_agent()
            ],
            tasks=[solver_task, research_task, summary_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the final workflow
        result = final_crew.kickoff()
        return result 