from typing import Any, Dict

from graph.state import GraphState
from langchain.schema import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from utils.logging import get_app_logger

logger = get_app_logger()
web_search_tool = TavilySearchResults(max_results=3)


def web_search(state: GraphState) -> Dict[str, Any]:
    logger.info("Searching on the web")
    question = state["question"]
    documents = state.get("documents")

    tavily_results = web_search_tool.invoke({"query": question})
    joined_tavily_result = "\n".join(
        [tavily_result["content"] for tavily_result in tavily_results]
    )
    web_results = Document(page_content=joined_tavily_result)
    if documents is not None:
        documents.append(web_results)
    else:
        documents = [web_results]
    return {"documents": documents, "question": question}


if __name__ == "__main__":
    web_search(state={"question": "agent memory", "documents": None})
