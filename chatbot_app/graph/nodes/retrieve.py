from typing import Any, Dict

from graph.state import GraphState
from graph.utils import (
    decompose_query,
    get_chroma_retriever,
    get_history_aware_retriever,
)
from utils.logging import get_app_logger

logger = get_app_logger()

chroma_retriever = get_chroma_retriever(top_k=5, score_threshold=0.5)
retriever = get_history_aware_retriever(chroma_retriever)


def retrieve(state: GraphState) -> Dict[str, Any]:
    logger.info("Retrieving the documents from the vector database")
    question = state["question"]
    documents = []
    chat_history = state.get("chat_history")
    if not chat_history:
        chat_history = []
    try:
        sub_queries = decompose_query(question)
        for sub_query in sub_queries:
            documents += retriever.invoke(
                {"input": sub_query.query, "chat_history": chat_history}
            )
    except Exception as e:
        logger.debug(
            f"Fallback to default retrieval. Exception occured while retrieving documents exception: {e}"
        )
        documents = retriever.invoke(
            {"input": sub_query.query, "chat_history": chat_history}
        )

    return {"documents": documents, "question": question}
