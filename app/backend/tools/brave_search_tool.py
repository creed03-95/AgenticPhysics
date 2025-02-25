from langchain.tools import Tool
import requests
import os
from typing import Dict, List
from config import BRAVE_SEARCH_API_KEY

class BraveSearchTool:
    def __init__(self):
        self.api_key = BRAVE_SEARCH_API_KEY
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        
    def search(self, query: str) -> str:
        """
        Perform a search using Brave Search API
        """
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query
            }
            
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Format web results
                for result in data.get("web", {}).get("results", [])[:5]:
                    results.append(
                        f"Title: {result.get('title', '')}\n"
                        f"Description: {result.get('description', '')}\n"
                        f"URL: {result.get('url', '')}\n"
                    )
                
                return "\n".join(results) if results else "No results found."
            else:
                return f"Error: API returned status code {response.status_code}"
            
        except Exception as e:
            return f"Error performing search: {str(e)}"
    
    def get_tool(self) -> Tool:
        """
        Create and return the Brave search tool
        """
        return Tool(
            name="brave_search",
            func=self.search,
            description="""Use this tool to search for information about heat equations,
            numerical methods, and related topics using Brave Search."""
        ) 