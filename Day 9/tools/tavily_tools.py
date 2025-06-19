"""
Tavily Search Tools for the 5 Pillar Resume OKR Agent

This module provides search functionality using Tavily API
to retrieve high-quality examples of aligned OKRs and resume content.
"""

from langchain_tavily import TavilySearch
from typing import List, Dict, Any

# ------------------------------------------
# Tool Creation Functions
# ------------------------------------------

def create_resume_example_search_tool(max_results: int = 3) -> TavilySearch:
    """
    Create a Tavily search tool configured to find high-quality resume examples
    
    Args:
        max_results (int): Number of results to return
        
    Returns:
        TavilySearch: Configured tool
    """
    return TavilySearch(max_results=max_results)

def create_okr_alignment_search_tool(max_results: int = 5) -> TavilySearch:
    """
    Create a Tavily search tool configured to find OKR-outcome alignment examples
    
    Args:
        max_results (int): Number of results to return
        
    Returns:
        TavilySearch: Configured tool
    """
    return TavilySearch(max_results=max_results, search_depth="advanced")

# ------------------------------------------
# Bundled Tool Loader
# ------------------------------------------

def get_5pillar_search_tools() -> List[TavilySearch]:
    """
    Returns the specific tools for the 5 Pillar resume OKR validation task
    
    Returns:
        List[TavilySearch]: List of search tools
    """
    resume_search_tool = create_resume_example_search_tool()
    okr_search_tool = create_okr_alignment_search_tool()
    
    return [resume_search_tool, okr_search_tool]

# ------------------------------------------
# Unified Search Invocation
# ------------------------------------------

def search_with_tavily_tool(tool: TavilySearch, query: str) -> Dict[str, Any]:
    """
    Run a Tavily search with the given tool and query string
    
    Args:
        tool (TavilySearch): Configured Tavily tool
        query (str): User search query
        
    Returns:
        Dict[str, Any]: Search results or error
    """
    try:
        results = tool.invoke(query)
        return results
    except Exception as e:
        return {
            "error": str(e),
            "query": query
        }

# ------------------------------------------
# Predefined Query Functions
# ------------------------------------------

def get_resume_example_query(pillar_name: str) -> str:
    """
    Generate a Tavily search query for resume examples for a specific pillar
    
    Args:
        pillar_name (str): One of the 5 pillars
        
    Returns:
        str: Query string
    """
    return f"Example resume section for '{pillar_name}' in student profile"

def get_okr_alignment_query() -> str:
    """
    Query to find examples of well-aligned student OKRs and outcomes
    
    Returns:
        str: Query string
    """
    return "Examples of student OKRs and aligned outcomes or project submissions"
