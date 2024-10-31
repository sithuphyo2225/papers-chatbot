from typing import Any, Dict

from graph.chains.retrieval_grader import retrieval_grader
from graph.state import GraphState
from utils.logging import get_app_logger

logger = get_app_logger()


def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, we will set a flag to run web search

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Filtered out irrelevant documents and updated web_search state
    """

    logger.info("Check doucment relevant to the question")
    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    web_search = False
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade.lower() == "yes":
            logger.info("GRADE: Document relevant")
            filtered_docs.append(d)
        else:
            logger.info("GRADE: Document not relevant")
            web_search = True
            continue
    return {"documents": filtered_docs, "question": question, "web_search": web_search}
