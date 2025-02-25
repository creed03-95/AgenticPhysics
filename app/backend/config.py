"""
Centralized configuration for API keys and LLM settings.
"""
import os
from crewai import LLM

# API Keys
BRAVE_SEARCH_API_KEY = "BSAkO9qV_cSR8p6OKlhfSfogcfK0ZQE"
OPENAI_API_KEY = "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"

# Set environment variables for other libraries that might need them
os.environ["BRAVE_API_KEY"] = BRAVE_SEARCH_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# LLM Configuration
DEFAULT_LLM = LLM(
    model="gpt-4o",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)

# Agent-specific LLM configurations
RESEARCH_LLM = LLM(
    model="gpt-4o",
    temperature=0.7,  # Higher temperature for more creative research
    api_key=OPENAI_API_KEY
)

METRICS_LLM = LLM(
    model="gpt-4o",
    temperature=0.2,  # Lower temperature for more precise metric analysis
    api_key=OPENAI_API_KEY
)

SUMMARIZER_LLM = LLM(
    model="gpt-4o",
    temperature=0.5,  # Balanced temperature for clear explanations
    api_key=OPENAI_API_KEY
) 