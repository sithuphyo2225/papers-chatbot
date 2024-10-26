from typing import Any, Dict

from graph.chains.generation import generation_chain
from graph.state import GraphState
from langchain_core.messages import AIMessage, HumanMessage
from utils.logging import get_app_logger

logger = get_app_logger()


def generate(state: GraphState) -> Dict[str, Any]:
    logger.info("Generate the output")
    question = state["question"]
    documents = state["documents"]
    chat_history = state.get("chat_history")
    if not chat_history:
        chat_history = []
    generation = generation_chain.invoke(
        {"question": question, "documents": documents, "chat_history": chat_history}
    )

    return {
        "documents": documents,
        "question": question,
        "generation": generation,
        "chat_history": [
            HumanMessage(state["question"]),
            AIMessage(generation),
        ],
    }
