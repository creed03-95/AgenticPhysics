from crewai import Agent, Task
from tools.brave_search_tool import BraveSearchTool
from tools.arxiv_tool import ArxivTool
from services.ranking_service import RankingService
from prompts.prompt import RESEARCH_AGENT, VTK_RESEARCH_TASK_TEMPLATE, TEXT_RESEARCH_TASK_TEMPLATE
from config import RESEARCH_LLM
from typing import Dict, Any, Optional, List
import asyncio

class ResearchAgent:
    def __init__(self):
        self.brave_search_tool = BraveSearchTool()
        self.arxiv_tool = ArxivTool()
        self.ranking_service = RankingService()
    
    def get_agent(self) -> Agent:
        """
        Create and return the research agent with enhanced configuration
        """
        return Agent(
            role=RESEARCH_AGENT["role"],
            goal=RESEARCH_AGENT["goal"],
            backstory=RESEARCH_AGENT["backstory"],
            tools=[
                self.brave_search_tool.get_tool(),
                self.arxiv_tool.get_tool()
            ],
            llm=RESEARCH_LLM,
            verbose=True,
            memory=True,  # Enable memory for context retention
            respect_context_window=True,  # Prevent token limit issues
            max_rpm=10  # Rate limiting for API stability
        )
    
    def perform_research(self, query: str, metrics: Dict[str, Any] = None) -> str:
        """
        Perform research using both tools and rank results
        """
        # Get results from both sources
        brave_results = self.brave_search_tool.search(query)
        arxiv_results = self.arxiv_tool.search_papers(query)
        
        # Rank and format results
        ranked_results = self.ranking_service.rank_results(
            brave_results=brave_results,
            arxiv_results=arxiv_results,
            query=query,
            metrics=metrics
        )
        
        return self.ranking_service.format_ranked_results(ranked_results)
    
    def create_vtk_research_task(self, metrics: Dict[str, Any], question: str, context: Optional[List[Task]] = None) -> Task:
        """
        Create research task for VTK file analysis
        """
        # Format metrics for search
        search_metrics = []
        for key, value in metrics.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, (int, float)):
                        search_metrics.append(f"{key} {subkey}: {subvalue}")
        
        metrics_str = ", ".join(search_metrics)
        
        # Get metrics analysis from context if available
        metrics_analysis = ""
        if context and len(context) > 0:
            metrics_analysis = f"\nMetrics Analysis:\n{context[0].output}\n"
        
        return Task(
            description=(
                f"Research the following heat equation problem:\n"
                f"Question: {question}\n"
                f"Key metrics: {metrics_str}\n"
                f"{metrics_analysis}"
                "Focus on numerical methods, heat equation theory, and physical interpretation."
            ),
            expected_output=(
                "A comprehensive research analysis including:\n"
                "1. Mathematical foundations\n"
                "2. Similar case studies\n"
                "3. Physical phenomena explanation\n"
                "4. Practical implications"
            ),
            agent=self.get_agent(),
            context=context
        )
    
    def create_text_research_task(self, question: str) -> Task:
        """
        Create research task for direct text questions
        """
        return Task(
            description=(
                f"Research this heat equation question:\n"
                f"{question}\n"
                "Focus on mathematical theory, physical interpretation, and applications."
            ),
            expected_output=(
                "A detailed analysis including:\n"
                "1. Theoretical background\n"
                "2. Solution methods\n"
                "3. Physical significance\n"
                "4. Real-world applications"
            ),
            agent=self.get_agent()
        ) 