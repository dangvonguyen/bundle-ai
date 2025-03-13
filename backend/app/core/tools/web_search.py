import os
from typing import Any, Optional

import httpx
from langchain.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field

# Used to tell the model how/when/why to use the tool.
# You can provide few-shot examples as a part of the description.
WEB_SEARCH_DESCRIPTION = """
Useful when you want to find information in the web
"""

TAVILY_API_URL = "https://api.tavily.com"


class WebSearchArgs(BaseModel):
    """
    Input arguments for web search tool.
    """

    query: str = Field(description="The search query to look up")
    num_results: int = Field(description="Number of search results to return")


class WebSearchTool(BaseTool):
    """
    Tool for performing web searches.
    """

    name: str = "web_search"
    description: str = WEB_SEARCH_DESCRIPTION
    args_schema: type[BaseModel] = WebSearchArgs

    def _run(
        self,
        query: str,
        results: int,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> None:
        pass

    async def _arun(
        self,
        query: str,
        num_results: int,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> list[dict[str, Any]]:
        payload = {
            "api_key": os.getenv("TAVILY_API_KEY"),
            "query": query,
            "max_results": num_results,
        }

        async def fetch() -> dict[str, Any]:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{TAVILY_API_URL}/search", json=payload)

                data: dict[str, Any] = response.json()
                if response.status_code == 200:
                    return data
                else:
                    raise Exception(f"{data['detail']['error']}")

        data = await fetch()

        results = []
        if isinstance(data.get("results"), list):
            for result in data["results"]:
                if isinstance(result, dict):
                    results.append(
                        {
                            "title": result.get("title"),
                            "url": result.get("url"),
                            "content": result.get("content"),
                        }
                    )

        return results
