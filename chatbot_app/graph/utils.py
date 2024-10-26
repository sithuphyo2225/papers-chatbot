from typing import List

from langchain.chains import create_history_aware_retriever
from langchain.output_parsers import PydanticToolsParser
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field


class SubQuery(BaseModel):
    """Represents a specific search query for research paper databases."""

    query: str = Field(..., description="A very specific query against the database.")


# Define the system prompt template
system_prompt = (
    "You are a helpful assistant that generates multiple sub-questions related to an input question. "
    "The goal is to break down the input into a set of sub-problems or sub-questions that can be answered in isolation. "
    "Perform query decomposition. Given a user question, break it down into distinct sub-questions needed "
    "to answer the original question. If there are unfamiliar acronyms or words, retain them as they are."
)
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("human", "{question}")]
)

# Initialize language model, tools, and parser
llm = ChatOpenAI(temperature=0)
llm_with_tools = llm.bind_tools([SubQuery])
parser = PydanticToolsParser(tools=[SubQuery])

# Pipeline for query analysis
query_analyzer = prompt_template | llm_with_tools | parser


def decompose_query(question: str) -> List[SubQuery]:
    """Decompose a given question into a list of sub-queries."""
    return query_analyzer.invoke(question)


def get_chroma_retriever(
    top_k: int = 5, score_threshold: float = 0.5
) -> VectorStoreRetriever:
    """Retrieve research papers based on similarity score using Chroma."""
    retriever = Chroma(
        collection_name="papers",
        persist_directory=".chroma",
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
    ).as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": top_k, "score_threshold": score_threshold},
    )
    return retriever


def get_history_aware_retriever(retriever):
    ### Contextualize question ###
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever
