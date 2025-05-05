from langchain_community.tools.tavily_search import TavilySearchResults

import os

def get_web_search_tool():
    return TavilySearchResults(api_key=os.getenv("TAVILY_API_KEY"))
