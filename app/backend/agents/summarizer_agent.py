from crewai import Agent
from tools.visualization_tool import VisualizationTool
from tools.interpretation_tool import InterpretationTool
from prompts.prompt import SUMMARIZER_AGENT
from config import SUMMARIZER_LLM

class SummarizerAgent:
    def __init__(self):
        self.visualization_tool = VisualizationTool()
        self.interpretation_tool = InterpretationTool()
    
    def get_agent(self) -> Agent:
        """
        Create and return the summarizer agent with enhanced configuration
        """
        return Agent(
            role=SUMMARIZER_AGENT["role"],
            goal=SUMMARIZER_AGENT["goal"],
            backstory=SUMMARIZER_AGENT["backstory"],
            tools=[
                self.visualization_tool.get_tool(),
                self.interpretation_tool.get_tool()
            ],
            llm=SUMMARIZER_LLM,
            verbose=True,
            memory=True,  # Enable memory for context retention
            respect_context_window=True,  # Prevent token limit issues
            max_rpm=10  # Rate limiting for API stability
        ) 