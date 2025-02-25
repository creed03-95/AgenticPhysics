from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RankingService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def rank_results(self, 
                    brave_results: List[Dict[str, str]], 
                    arxiv_results: List[Dict[str, str]], 
                    query: str,
                    metrics: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Rank combined results from Brave Search and arXiv based on relevance
        """
        # Combine results with source information
        combined_results = []
        for result in brave_results:
            combined_results.append({
                **result,
                "source": "brave",
                "score": 0.0
            })
        for result in arxiv_results:
            combined_results.append({
                **result,
                "source": "arxiv",
                "score": 0.0
            })
        
        if not combined_results:
            return []
        
        # Prepare texts for TF-IDF
        texts = []
        for result in combined_results:
            # Combine title and description/summary for better matching
            if "title" in result and "description" in result:  # Brave results
                text = f"{result['title']} {result['description']}"
            else:  # arXiv results
                text = f"{result['title']} {result['summary']}"
            texts.append(text)
        
        # Add query to texts for comparison
        texts.append(query)
        
        try:
            # Calculate TF-IDF and cosine similarity
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            cosine_similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]
            
            # Update scores
            for idx, score in enumerate(cosine_similarities):
                combined_results[idx]["score"] = float(score)
            
            # Apply source-specific boosts
            for result in combined_results:
                # Boost arXiv results for theoretical/mathematical questions
                if result["source"] == "arxiv" and any(term in query.lower() 
                    for term in ["theory", "equation", "mathematical", "derivation"]):
                    result["score"] *= 1.2
                
                # Boost Brave results for practical/application questions
                if result["source"] == "brave" and any(term in query.lower() 
                    for term in ["example", "practical", "application", "real-world"]):
                    result["score"] *= 1.2
            
            # If metrics are provided, boost results that mention similar values
            if metrics:
                for result in combined_results:
                    text = texts[combined_results.index(result)].lower()
                    for metric_type, metric_data in metrics.items():
                        if isinstance(metric_data, dict):
                            for key, value in metric_data.items():
                                if isinstance(value, (int, float)):
                                    # Check if the text mentions similar values
                                    value_str = f"{value:.2f}"
                                    if value_str in text:
                                        result["score"] *= 1.1
            
            # Sort by score
            ranked_results = sorted(combined_results, key=lambda x: x["score"], reverse=True)
            
            # Take top results and format them
            top_results = ranked_results[:5]  # Adjust number as needed
            
            return top_results
            
        except Exception as e:
            print(f"Error in ranking: {str(e)}")
            # Return original results if ranking fails
            return combined_results[:5]
    
    def format_ranked_results(self, ranked_results: List[Dict[str, Any]]) -> str:
        """
        Format ranked results into a readable string
        """
        formatted_results = []
        for result in ranked_results:
            if result["source"] == "brave":
                formatted_results.append(
                    f"[Web Source] Score: {result['score']:.2f}\n"
                    f"Title: {result['title']}\n"
                    f"Description: {result['description']}\n"
                    f"URL: {result['url']}\n"
                )
            else:  # arxiv
                formatted_results.append(
                    f"[Academic Paper] Score: {result['score']:.2f}\n"
                    f"Title: {result['title']}\n"
                    f"Authors: {result['authors']}\n"
                    f"Summary: {result['summary']}\n"
                    f"URL: {result['url']}\n"
                )
        
        return "\n".join(formatted_results) 