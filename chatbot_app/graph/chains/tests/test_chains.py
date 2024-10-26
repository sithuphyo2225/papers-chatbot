from pprint import pprint

from graph.chains.generation import generation_chain
from graph.chains.hallucination_grader import GradeHallucinations, hallucination_grader
from graph.chains.retrieval_grader import GradeDocument, retrieval_grader
from graph.chains.router import RouteQuery, question_router
from graph.utils import get_chroma_retriever, get_history_aware_retriever

chroma_retriever = get_chroma_retriever(top_k=5, score_threshold=0.5)
retriever = get_history_aware_retriever(chroma_retriever)


def test_retrival_grader_answer_yes() -> None:
    question = "A survey on deep learning approaches for text-to-SQL"
    docs = retriever.invoke({"input": question, "chat_history": []})
    doc_txt = docs[1].page_content

    res: GradeDocument = retrieval_grader.invoke(
        {"question": question, "document": doc_txt}
    )

    assert res.binary_score == "yes"


def test_retrival_grader_answer_no() -> None:
    question = "A survey on deep learning approaches for text-to-SQL"
    docs = retriever.invoke({"input": question, "chat_history": []})
    doc_txt = docs[1].page_content

    res: GradeDocument = retrieval_grader.invoke(
        {"question": "how to make pizaa", "document": doc_txt}
    )

    assert res.binary_score == "no"


def test_generation_chain() -> None:
    question = "A survey on deep learning approaches for text-to-SQL"

    docs = retriever.invoke({"input": question, "chat_history": []})
    generation = generation_chain.invoke(
        {"documents": docs, "question": question, "chat_history": []}
    )
    pprint(generation)


def test_hallucination_grader_answer_no() -> None:
    question = "A survey on deep learning approaches for text-to-SQL"
    docs = retriever.invoke({"input": question, "chat_history": []})

    res: GradeHallucinations = hallucination_grader.invoke(
        {
            "documents": docs,
            "generation": "A survey on deep learning approaches for text-to-SQL George Katsogiannis-Meimarakis1 · Georgia Koutrika1 Received: 27 May 2022 / Revised: 31 October 2022 / Accepted: 10 December 2022 / Published online: 23 January 2023 © The Author(s) 2023",
            "chat_history": [],
        }
    )
    assert not res.binary_score


def test_router_to_vectorstore() -> None:
    question = "A survey on deep learning approaches for text-to-SQL"

    res: RouteQuery = question_router.invoke({"question": question})
    assert res.datasource == "vectorstore"


def test_router_to_websearch() -> None:
    question = "how to make pizza"

    res: RouteQuery = question_router.invoke({"question": question})
    assert res.datasource == "websearch"
