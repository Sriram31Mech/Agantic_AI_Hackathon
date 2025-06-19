"""
Tavily Search Tools for the Agent
This module provides search functionality using Tavily API
"""

from langchain_tavily import TavilySearch
from typing import List, Dict, Any

def create_search_tool(max_results: int = 2) -> TavilySearch:
    """
    Create a Tavily search tool with specified configuration
    
    Args:
        max_results (int): Maximum number of search results to return
        
    Returns:
        TavilySearch: Configured search tool
    """
    return TavilySearch(max_results=max_results)

def create_advanced_search_tool(max_results: int = 5, search_depth: str = "advanced") -> TavilySearch:
    """
    Create an advanced Tavily search tool with more comprehensive results
    
    Args:
        max_results (int): Maximum number of search results to return
        search_depth (str): Search depth - "basic" or "advanced"
        
    Returns:
        TavilySearch: Configured advanced search tool
    """
    return TavilySearch(max_results=max_results, search_depth=search_depth)

def get_search_tools() -> List[TavilySearch]:
    """
    Get a list of configured search tools
    
    Returns:
        List[TavilySearch]: List of search tools
    """
    basic_search = create_search_tool(max_results=2)
    advanced_search = create_advanced_search_tool(max_results=5)
    
    return [basic_search, advanced_search]

def search_with_tool(tool: TavilySearch, query: str) -> Dict[str, Any]:
    """
    Execute a search using the provided tool
    
    Args:
        tool (TavilySearch): The search tool to use
        query (str): Search query
        
    Returns:
        Dict[str, Any]: Search results
    """
    try:
        results = tool.invoke(query)
        return results
    except Exception as e:
        return {"error": str(e), "query": query}

