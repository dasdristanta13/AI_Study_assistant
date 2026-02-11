"""
Web Search Utilities
Handles web searching and content extraction using Tavily and Firecrawl
"""
import os
from typing import List, Optional
from tavily import TavilyClient
from langchain.schema import Document


class WebSearcher:
    """Handle web search and content extraction"""
    
    def __init__(self, tavily_api_key: Optional[str] = None):
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        
        if self.tavily_api_key:
            self.client = TavilyClient(api_key=self.tavily_api_key)
        else:
            self.client = None
    
    def search(self, query: str, max_results: int = 5) -> List[Document]:
        """Search the web and return results as documents"""
        if not self.client:
            raise ValueError("Tavily API key not configured")
        
        try:
            # Perform search
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
            
            documents = []
            
            # Process results
            if "results" in response:
                for result in response["results"]:
                    doc = Document(
                        page_content=result.get("content", ""),
                        metadata={
                            "source": result.get("url", ""),
                            "title": result.get("title", ""),
                            "score": result.get("score", 0)
                        }
                    )
                    documents.append(doc)
            
            return documents
            
        except Exception as e:
            raise Exception(f"Web search failed: {str(e)}")
    
    def get_page_content(self, url: str) -> str:
        """Extract content from a specific URL"""
        if not self.client:
            raise ValueError("Tavily API key not configured")
        
        try:
            # Use Tavily's extract endpoint
            response = self.client.extract(urls=[url])
            
            if response and "results" in response and len(response["results"]) > 0:
                return response["results"][0].get("raw_content", "")
            
            return ""
            
        except Exception as e:
            raise Exception(f"Content extraction failed: {str(e)}")
    
    def search_and_summarize(self, query: str) -> dict:
        """Search and get AI-generated summary from Tavily"""
        if not self.client:
            raise ValueError("Tavily API key not configured")
        
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                include_answer=True
            )
            
            return {
                "answer": response.get("answer", ""),
                "sources": [r.get("url") for r in response.get("results", [])],
                "content": "\n\n".join([r.get("content", "") for r in response.get("results", [])])
            }
            
        except Exception as e:
            raise Exception(f"Search and summarize failed: {str(e)}")


class URLContentExtractor:
    """Extract content from URLs"""
    
    def __init__(self, firecrawl_api_key: Optional[str] = None):
        self.firecrawl_api_key = firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY")
        self.firecrawl_available = False
        
        # Try to import and initialize Firecrawl
        if self.firecrawl_api_key:
            try:
                from firecrawl import FirecrawlApp
                self.firecrawl = FirecrawlApp(api_key=self.firecrawl_api_key)
                self.firecrawl_available = True
            except ImportError:
                print("Firecrawl not available, will use Tavily fallback")
    
    def extract_from_url(self, url: str) -> Document:
        """Extract content from a URL using Firecrawl or fallback"""
        if self.firecrawl_available:
            try:
                # Use Firecrawl for better content extraction
                result = self.firecrawl.scrape_url(url, params={'formats': ['markdown']})
                
                content = result.get('markdown', '') or result.get('content', '')
                
                return Document(
                    page_content=content,
                    metadata={
                        "source": url,
                        "title": result.get('title', ''),
                        "extractor": "firecrawl"
                    }
                )
            except Exception as e:
                print(f"Firecrawl extraction failed, using fallback: {e}")
        
        # Fallback to Tavily
        searcher = WebSearcher()
        content = searcher.get_page_content(url)
        
        return Document(
            page_content=content,
            metadata={
                "source": url,
                "extractor": "tavily"
            }
        )