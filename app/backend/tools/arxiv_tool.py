from langchain.tools import Tool
import arxiv
from typing import List, Dict

class ArxivTool:
    def search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search for relevant papers on arXiv
        """
        try:
            # Create search client
            client = arxiv.Client()
            
            # Build search query
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            # Execute search
            results = []
            for paper in client.results(search):
                results.append({
                    "title": paper.title,
                    "authors": ", ".join(author.name for author in paper.authors),
                    "summary": paper.summary,
                    "url": paper.pdf_url,
                    "published": paper.published.strftime("%Y-%m-%d")
                })
            
            return results
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_tool(self) -> Tool:
        """
        Create and return the arXiv tool
        """
        return Tool(
            name="arxiv_search",
            func=self.search_papers,
            description="""Use this tool to search for research papers about heat
            equations and numerical methods on arXiv."""
        ) 