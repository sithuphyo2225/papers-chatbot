import uuid
from typing import Annotated, List, Sequence, TypedDict, Union, cast

from langchain_core.messages import (
    BaseMessage,
    BaseMessageChunk,
    MessageLikeRepresentation,
    RemoveMessage,
    convert_to_messages,
    message_chunk_to_message,
)

Messages = Union[list[MessageLikeRepresentation], MessageLikeRepresentation]


def add_messages(left: Messages, right: Messages) -> Messages:
    """Merges two lists of messages, updating existing messages by ID.

    By default, this ensures the state is "append-only", unless the
    new message has the same ID as an existing message.

    Args:
        left: The base list of messages.
        right: The list of messages (or single message) to merge
            into the base list.

    Returns:
        A new list of messages with the messages from `right` merged into `left`.
        If a message in `right` has the same ID as a message in `left`, the
        message from `right` will replace the message from `left`.
        If right messages list is empty, will return empty list to clear the message history
    """

    # coerce to list
    if not isinstance(left, list):
        left = [left]  # type: ignore[assignment]
    if not isinstance(right, list):
        right = [right]  # type: ignore[assignment]

    if right == []:
        return []

    # coerce to message
    left = [
        message_chunk_to_message(cast(BaseMessageChunk, m))
        for m in convert_to_messages(left)
    ]
    right = [
        message_chunk_to_message(cast(BaseMessageChunk, m))
        for m in convert_to_messages(right)
    ]
    # assign missing ids
    for m in left:
        if m.id is None:
            m.id = str(uuid.uuid4())
    for m in right:
        if m.id is None:
            m.id = str(uuid.uuid4())
    # merge
    left_idx_by_id = {m.id: i for i, m in enumerate(left)}
    merged = left.copy()
    ids_to_remove = set()
    for m in right:
        if (existing_idx := left_idx_by_id.get(m.id)) is not None:
            if isinstance(m, RemoveMessage):
                ids_to_remove.add(m.id)
            else:
                merged[existing_idx] = m
        else:
            if isinstance(m, RemoveMessage):
                raise ValueError(
                    f"Attempting to delete a message with an ID that doesn't exist ('{m.id}')"
                )

            merged.append(m)
    merged = [m for m in merged if m.id not in ids_to_remove]
    return merged


class GraphState(TypedDict):
    """
    Represents a graph state

    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to add search
        documents: list of documents
        chat_history: list of chat history
    """

    question: str
    generation: str
    web_search: bool
    documents: List[str]
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
