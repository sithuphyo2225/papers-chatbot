from graph.chains.answer_grader import answer_grader
from graph.chains.hallucination_grader import hallucination_grader
from graph.chains.router import RouteQuery, question_router
from graph.consts import GENERATE, GRADE_DOCUMENTS, RETRIEVE, WEBSEARCH
from graph.nodes import generate, grade_documents, retrieve, web_search
from graph.state import GraphState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langsmith import Client
from utils.logging import get_app_logger

logger = get_app_logger()
langsmith_client = Client()


def decide_to_generate(state):
    logger.info("Assessing graded documents")

    if state["web_search"]:
        logger.info("Decision: Web search needed")
        return WEBSEARCH
    else:
        logger.info("Decision: Generate response")
        return GENERATE


def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    logger.info("Checking for hallucinations")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    chat_history = state.get("chat_history", None)
    if not chat_history:
        chat_history = []

    hallucination_grade = hallucination_grader.invoke(
        {"documents": documents, "generation": generation, "chat_history": chat_history}
    )

    answer_grade = answer_grader.invoke(
        {"question": question, "generation": generation}
    )

    if hallucination_grade.binary_score or answer_grade.binary_score:
        logger.info("Decision: Generation is grounded")
        return END
    else:
        logger.info("Decision: Generation not grounded, retry")
        return GENERATE


def route_question(state: GraphState) -> str:
    logger.info("Routing question")
    question = state["question"]
    source: RouteQuery = question_router.invoke({"question": question})
    if source.datasource == WEBSEARCH:
        logger.info("Route to web search")
        return WEBSEARCH
    elif source.datasource == "vectorstore":
        logger.info("Route to RAG")
        return RETRIEVE


workflow = StateGraph(GraphState)

workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)
workflow.add_node(WEBSEARCH, web_search)

workflow.set_conditional_entry_point(
    route_question,
    {
        WEBSEARCH: WEBSEARCH,
        RETRIEVE: RETRIEVE,
    },
)
workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)
workflow.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
)

workflow.add_conditional_edges(
    GENERATE, grade_generation_grounded_in_documents_and_question
)
workflow.add_edge(WEBSEARCH, GENERATE)
workflow.add_edge(GENERATE, END)

memory = MemorySaver()
graph_flow = workflow.compile(checkpointer=memory)

graph_flow.get_graph().draw_mermaid_png(output_file_path="graph.png")
